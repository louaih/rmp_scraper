import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException
from webdriver_manager.firefox import GeckoDriverManager
import time
import json
from openai import OpenAI  # Import OpenAI directly
import os
from dotenv import load_dotenv
import logging
from functools import wraps
import random

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def retry_on_failure(max_retries=3, delay=2):
    """Decorator to retry a function on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logging.error(f"Failed after {max_retries} attempts: {e}")
                        raise
                    logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay + random.uniform(0, 1))  # Add jitter
            return None
        return wrapper
    return decorator

class ReviewScraper:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        try:
            self.openai_client = OpenAI()
            # Test API access
            self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            logging.info("Successfully initialized OpenAI client with valid API access")
        except Exception as e:
            if "insufficient_quota" in str(e):
                logging.error("OpenAI API quota exceeded or no access. Please check your billing details and ensure you have a paid account.")
            else:
                logging.error(f"Failed to initialize OpenAI client: {e}")
            raise
        
        self.setup_driver()
        
    def setup_driver(self):
        """Set up the Firefox browser driver with appropriate options"""
        try:
            # Configure Firefox options
            firefox_options = Options()
            firefox_options.add_argument('--headless')
            firefox_options.add_argument('--disable-gpu')
            firefox_options.add_argument('--no-sandbox')
            firefox_options.add_argument('--disable-dev-shm-usage')
            
            # Use webdriver_manager to handle GeckoDriver
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
            
            # Set timeouts
            self.driver.set_page_load_timeout(60)  # Increased timeout
            self.driver.implicitly_wait(10)
            
        except WebDriverException as e:
            logging.error(f"Error setting up Firefox WebDriver: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error setting up driver: {e}")
            raise

    @retry_on_failure(max_retries=3, delay=5)
    def scrape_reviews(self, url):
        """Scrape all reviews from a professor's RMP page"""
        logging.info(f"Scraping reviews from: {url}")
        reviews = []
        
        try:
            # Navigate to the page with retry logic
            try:
                self.driver.get(url)
            except TimeoutException:
                logging.warning("Page load timed out, but continuing...")
            
            # Wait for any review content to load
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((
                        By.XPATH, 
                        "//div[contains(@class, 'Rating__RatingBody')]"
                    ))
                )
            except TimeoutException:
                logging.warning("Reviews did not load within timeout, but continuing...")
            
            # Get all review cards
            review_cards = []
            try:
                review_cards = self.driver.find_elements(
                    By.XPATH, 
                    "//div[contains(@class, 'Rating__RatingBody')]"
                )
                logging.info(f"Found {len(review_cards)} review cards")
            except StaleElementReferenceException:
                logging.warning("Stale element reference when finding review cards, retrying...")
                review_cards = self.driver.find_elements(
                    By.XPATH, 
                    "//div[contains(@class, 'Rating__RatingBody')]"
                )
            
            for card in review_cards:
                try:
                    # Get review text
                    try:
                        review_text = card.find_element(
                            By.XPATH, 
                            ".//div[contains(@class, 'Comments__StyledComments')]"
                        ).text
                        logging.debug("Successfully found review text")
                    except NoSuchElementException:
                        logging.warning("Could not find review text")
                        review_text = "No review text available"
                    
                    # Get timestamp
                    try:
                        timestamp = card.find_element(
                            By.XPATH, 
                            ".//div[contains(@class, 'TimeStamp__StyledTimeStamp')]"
                        ).text
                        logging.debug(f"Found timestamp: {timestamp}")
                    except NoSuchElementException:
                        logging.warning("Could not find timestamp")
                        timestamp = "Unknown date"
                    
                    # Get quality and difficulty ratings
                    quality_rating = None
                    difficulty_rating = None
                    
                    try:
                        # Find all rating containers
                        rating_containers = card.find_elements(
                            By.XPATH, 
                            ".//div[contains(@class, 'CardNumRating__StyledCardNumRating')]"
                        )
                        logging.debug(f"Found {len(rating_containers)} rating containers")
                        
                        for container in rating_containers:
                            try:
                                # Get the label from CardNumRating__CardNumRatingHeader
                                label = container.find_element(
                                    By.XPATH,
                                    ".//div[contains(@class, 'CardNumRating__CardNumRatingHeader')]"
                                ).text.strip()
                                
                                # Get the value from CardNumRating__CardNumRatingNumber
                                value = container.find_element(
                                    By.XPATH,
                                    ".//div[contains(@class, 'CardNumRating__CardNumRatingNumber')]"
                                ).text.strip()
                                
                                logging.debug(f"Processing rating: {label} = {value}")
                                
                                if "QUALITY" in label.upper():
                                    try:
                                        quality_rating = float(value)
                                        logging.debug(f"Set quality rating to {quality_rating}")
                                    except ValueError:
                                        logging.warning(f"Could not convert quality value '{value}' to float")
                                elif "DIFFICULTY" in label.upper():
                                    try:
                                        difficulty_rating = float(value)
                                        logging.debug(f"Set difficulty rating to {difficulty_rating}")
                                    except ValueError:
                                        logging.warning(f"Could not convert difficulty value '{value}' to float")
                                else:
                                    logging.warning(f"Unknown rating label: {label}")
                            except Exception as e:
                                logging.warning(f"Error processing rating container: {e}")
                    except Exception as e:
                        logging.warning(f"Error finding rating containers: {e}")
                    
                    # Log the final ratings for this review
                    logging.info(f"Review ratings - Quality: {quality_rating}, Difficulty: {difficulty_rating}")
                    
                    reviews.append({
                        'text': review_text,
                        'timestamp': timestamp,
                        'quality_rating': quality_rating,
                        'difficulty_rating': difficulty_rating
                    })
                    
                except (NoSuchElementException, StaleElementReferenceException) as e:
                    logging.warning(f"Failed to scrape a review: {e}")
                    continue
                except Exception as e:
                    logging.error(f"Unexpected error while processing review: {e}")
                    continue
                    
            logging.info(f"Successfully scraped {len(reviews)} reviews")
            return {
                'reviews': reviews,
                'total_reviews': len(reviews)
            }
            
        except Exception as e:
            logging.error(f"Error scraping reviews for {url}: {e}")
            raise
            
    def analyze_reviews(self, reviews):
        """Use OpenAI to analyze and summarize the reviews"""
        if not reviews:
            return "No reviews available for analysis."
            
        # Combine all review texts with their quality and difficulty ratings
        all_reviews = "\n\n".join([
            f"Quality Rating: {review['quality_rating']}/5\n"
            f"Difficulty Rating: {review['difficulty_rating']}/5\n"
            f"Review: {review['text']}"
            for review in reviews
        ])
        
        # Create a prompt for the LLM
        prompt = f"""Please analyze the following professor reviews and provide a 150-word summary 
        that captures the main themes, strengths, and areas for improvement mentioned by students. 
        Focus on the most common patterns in the feedback while maintaining objectivity.
        Consider both the quality and difficulty ratings in your analysis.
        
        Reviews:
        {all_reviews}
        """
        
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an educational analyst summarizing professor reviews."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300
                )
                return response.choices[0].message.content
            except Exception as e:
                if "insufficient_quota" in str(e):
                    logging.error("OpenAI API quota exceeded. Please check your billing details.")
                    return "Analysis unavailable due to API quota limits."
                elif "rate_limit" in str(e) or "429" in str(e):
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)  # Exponential backoff
                        logging.warning(f"Rate limit hit. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                        time.sleep(wait_time)
                        continue
                    else:
                        logging.error("Max retries reached for rate limit. Skipping analysis.")
                        return "Analysis unavailable due to rate limits."
                else:
                    logging.error(f"Error analyzing reviews: {e}")
                    return "Error generating analysis."
        
        return "Error generating analysis after multiple retries."
            
    def process_all_professors(self):
        """Process all professors from the CSV file"""
        try:
            df = pd.read_csv('professor_ratings.csv')
            results = []
            
            for _, row in df.iterrows():
                logging.info(f"Processing reviews for {row['professor_name']}...")
                try:
                    review_data = self.scrape_reviews(row['url'])
                    
                    if review_data and review_data['reviews']:
                        try:
                            # Calculate averages, handling None values
                            quality_ratings = [r['quality_rating'] for r in review_data['reviews'] if r['quality_rating'] is not None]
                            difficulty_ratings = [r['difficulty_rating'] for r in review_data['reviews'] if r['difficulty_rating'] is not None]
                            
                            avg_quality = sum(quality_ratings) / len(quality_ratings) if quality_ratings else None
                            avg_difficulty = sum(difficulty_ratings) / len(difficulty_ratings) if difficulty_ratings else None
                            
                            # Add delay before analysis to avoid rate limits
                            time.sleep(2)
                            analysis = self.analyze_reviews(review_data['reviews'])
                            
                            if analysis.startswith("Analysis unavailable") or analysis.startswith("Error"):
                                logging.warning(f"Analysis failed for {row['professor_name']}")
                                analysis = "Analysis unavailable"
                            
                            results.append({
                                'professor_name': row['professor_name'],
                                'course_code': row['course_code'],
                                'number_of_reviews': len(review_data['reviews']),
                                'average_quality': avg_quality,
                                'average_difficulty': avg_difficulty,
                                'analysis': analysis
                            })
                            logging.info(f"Successfully scraped reviews for {row['professor_name']}")
                        except Exception as e:
                            logging.error(f"Error processing review data for {row['professor_name']}: {e}")
                            continue
                    else:
                        logging.warning(f"No reviews found for {row['professor_name']}")
                    
                    # Add random delay between requests
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logging.error(f"Failed to process {row['professor_name']}: {e}")
                    continue
                
            # Save results
            with open('professor_analyses.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
            # Also save as CSV
            analysis_df = pd.DataFrame(results)
            analysis_df.to_csv('professor_analyses.csv', index=False)
            logging.info("Successfully saved results to professor_analyses.json and professor_analyses.csv")
            
        except Exception as e:
            logging.error(f"Error processing professors: {e}")
            raise
            
    def close(self):
        """Close the browser driver"""
        try:
            self.driver.quit()
            logging.info("Successfully closed the browser driver")
        except Exception as e:
            logging.error(f"Error closing the browser driver: {e}")

if __name__ == "__main__":
    scraper = ReviewScraper()
    try:
        scraper.process_all_professors()
    finally:
        scraper.close() 