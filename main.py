import os
import sys
from src.professor_finder import RMPScraper
from src.review_analyzer import ReviewScraper
import pandas as pd
import logging
import json
import time

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Define paths
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
INPUT_DIR = os.path.join(DATA_DIR, 'input')
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')

# Ensure directories exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(PROJECT_ROOT, 'scraper.log')),
            logging.StreamHandler(sys.stdout)
        ]
    )

def get_course_codes():
    """Get course codes from user input or file"""
    if len(sys.argv) > 1:
        # Get course codes from command line arguments
        return sys.argv[1:]
    else:
        # Try to read from courses.txt
        courses_file = os.path.join(INPUT_DIR, 'courses.txt')
        try:
            with open(courses_file, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("Please provide course codes either as command line arguments or in a courses.txt file.")
            print("Example usage: python main.py CS101 MATH201")
            sys.exit(1)

def main():
    setup_logging()
    logging.info("Starting professor review analysis")
    
    # Get course codes
    course_codes = get_course_codes()
    logging.info(f"Analyzing professors for courses: {', '.join(course_codes)}")
    
    try:
        # Step 1: Find professors using professor_finder
        logging.info("Step 1: Finding professors for courses...")
        finder = RMPScraper()
        finder.courses = {code: f"Course {code}" for code in course_codes}  # Update courses to search
        finder.scrape_all_courses()
        logging.info("Successfully found professors and saved to professors.csv")
        
        # Step 2: Analyze reviews using review_analyzer
        logging.info("Step 2: Analyzing professor reviews...")
        analyzer = ReviewScraper()
        
        # Process each course
        all_results = []
        for course_code in course_codes:
            logging.info(f"Processing course: {course_code}")
            try:
                # Get professors for this course
                professors_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'professors.csv'))
                course_professors = professors_df[professors_df['course_code'] == course_code]
                
                if course_professors.empty:
                    logging.warning(f"No professors found for course {course_code}")
                    continue
                
                # Process each professor
                for _, professor in course_professors.iterrows():
                    try:
                        review_data = analyzer.scrape_reviews(professor['url'])
                        
                        if review_data and review_data['reviews']:
                            # Calculate averages
                            quality_ratings = [r['quality_rating'] for r in review_data['reviews'] if r['quality_rating'] is not None]
                            difficulty_ratings = [r['difficulty_rating'] for r in review_data['reviews'] if r['difficulty_rating'] is not None]
                            
                            avg_quality = sum(quality_ratings) / len(quality_ratings) if quality_ratings else None
                            avg_difficulty = sum(difficulty_ratings) / len(difficulty_ratings) if difficulty_ratings else None
                            
                            # Get analysis
                            analysis = analyzer.analyze_reviews(review_data['reviews'])
                            
                            if analysis.startswith("Analysis unavailable") or analysis.startswith("Error"):
                                logging.warning(f"Analysis failed for {professor['professor_name']}")
                                analysis = "Analysis unavailable"
                            
                            all_results.append({
                                'course_code': course_code,
                                'professor_name': professor['professor_name'],
                                'number_of_reviews': len(review_data['reviews']),
                                'average_quality': avg_quality,
                                'average_difficulty': avg_difficulty,
                                'analysis': analysis
                            })
                            logging.info(f"Successfully processed {professor['professor_name']} for {course_code}")
                        else:
                            logging.warning(f"No reviews found for {professor['professor_name']}")
                    except Exception as e:
                        logging.error(f"Error processing {professor['professor_name']}: {e}")
                        continue
                    
                    # Add delay between requests
                    time.sleep(2)
                
            except Exception as e:
                logging.error(f"Error processing course {course_code}: {e}")
                continue
        
        # Save results
        if all_results:
            # Save as JSON
            with open(os.path.join(OUTPUT_DIR, 'course_professor_analyses.json'), 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
            
            # Save as CSV
            results_df = pd.DataFrame(all_results)
            results_df.to_csv(os.path.join(OUTPUT_DIR, 'course_professor_analyses.csv'), index=False)
            
            logging.info("Successfully saved results to course_professor_analyses.json and course_professor_analyses.csv")
        else:
            logging.warning("No results were generated")
            
    except Exception as e:
        logging.error(f"Fatal error: {e}")
    finally:
        analyzer.close()

if __name__ == "__main__":
    main() 