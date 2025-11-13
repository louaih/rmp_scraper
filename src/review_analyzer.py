import pandas as pd
import time
import json
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
import random
import requests
import re
import base64

# Get the project root directory (two levels up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(PROJECT_ROOT, 'data', 'input')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'data', 'output')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ReviewScraper:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        try:
            # Initialize OpenAI client
            self.openai_client = OpenAI(api_key=api_key)

            # Test API access
            test_resp = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=10
            )

            # Basic check for a valid response
            if not test_resp or not test_resp.choices:
                raise ValueError("Empty response from OpenAI during initialization")

            logging.info("Successfully initialized OpenAI client with valid API access")
        except Exception as e:
            if "insufficient_quota" in str(e):
                logging.error("OpenAI API quota exceeded or no access. Please check your billing details and ensure you have a paid account.")
            else:
                logging.error(f"Failed to initialize OpenAI client: {e}")
            raise

    def extract_teacher_id_from_url(self, url):
        """Extract the teacher ID from the RateMyProfessors URL"""
        # URL format: https://www.ratemyprofessors.com/ShowRatings.jsp?tid=1234567
        # or newer format: https://www.ratemyprofessors.com/professor/1234567
        try:
            match = re.search(r'(?:tid=|professor/)(\d+)', url)
            if match:
                teacher_id = match.group(1)
                # Encode to base64 for the GraphQL ID
                encoded = base64.b64encode(f"Teacher-{teacher_id}".encode()).decode()
                logging.debug(f"Extracted teacher ID: {teacher_id}, encoded: {encoded}")
                return encoded
        except Exception as e:
            logging.warning(f"Could not extract teacher ID from URL {url}: {e}")
        return None

    def fetch_reviews_via_graphql(self, teacher_id_encoded, course_filter=None, max_reviews=None):
        """Fetch reviews using the RateMyProfessors GraphQL API with cursor-based pagination"""
        reviews = []
        cursor = None
        page_count = 0
        graphql_url = "https://www.ratemyprofessors.com/graphql"

        # Headers that mimic a real browser to avoid 403 Forbidden
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.6",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Origin": "https://www.ratemyprofessors.com",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "Referer": "https://www.ratemyprofessors.com/",
            "Sec-CH-UA": '"Chromium";v="142", "Brave";v="142", "Not_A Brand";v="99"',
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1"
        }

        graphql_query = """
        query RatingsListQuery(
          $count: Int!
          $id: ID!
          $courseFilter: String
          $cursor: String
        ) {
          node(id: $id) {
            __typename
            ... on Teacher {
              id
              legacyId
              firstName
              lastName
              numRatings
              school {
                id
                name
              }
              ratings(first: $count, after: $cursor, courseFilter: $courseFilter) {
                edges {
                  cursor
                  node {
                    id
                    comment
                    date
                    class
                    helpfulRating
                    clarityRating
                    difficultyRating
                    __typename
                  }
                }
                pageInfo {
                  hasNextPage
                  endCursor
                }
              }
            }
          }
        }
        """

        while True:
            page_count += 1
            logging.info(f"Fetching page {page_count} of reviews (cursor: {cursor})")

            variables = {
                "count": 20,  # Fetch more per request for efficiency
                "id": teacher_id_encoded,
                "courseFilter": course_filter,
                "cursor": cursor
            }

            payload = {
                "operationName": "RatingsListQuery",
                "query": graphql_query,
                "variables": variables
            }

            try:
                response = requests.post(graphql_url, json=payload, headers=headers, timeout=15)
                response.raise_for_status()
                data = response.json()

                # Check for GraphQL errors
                if "errors" in data:
                    logging.error(f"GraphQL error: {data['errors']}")
                    break

                # Extract ratings from response
                try:
                    ratings_connection = data['data']['node']['ratings']
                    edges = ratings_connection.get('edges', [])

                    for edge in edges:
                        node = edge['node']
                        reviews.append({
                            'text': node.get('comment', ''),
                            'timestamp': node.get('date', 'Unknown date'),
                            'quality_rating': node.get('clarityRating'),
                            'difficulty_rating': node.get('difficultyRating')
                        })

                    page_info = ratings_connection.get('pageInfo', {})
                    has_next_page = page_info.get('hasNextPage', False)
                    end_cursor = page_info.get('endCursor')

                    logging.info(f"Page {page_count}: fetched {len(edges)} reviews, total so far: {len(reviews)}")

                    if not has_next_page or not end_cursor:
                        logging.info(f"No more pages. Total reviews fetched: {len(reviews)}")
                        break

                    if max_reviews and len(reviews) >= max_reviews:
                        logging.info(f"Reached max_reviews limit ({max_reviews}). Stopping pagination.")
                        reviews = reviews[:max_reviews]
                        break

                    cursor = end_cursor
                    time.sleep(0.5)  # Small delay between requests

                except KeyError as e:
                    logging.error(f"Unexpected response structure: {e}")
                    logging.debug(f"Response: {data}")
                    break

            except Exception as e:
                logging.error(f"Error fetching reviews via GraphQL: {e}")
                if page_count == 1:
                    logging.error("Failed on first page, aborting pagination")
                    break
                else:
                    logging.warning(f"Error on page {page_count}, returning {len(reviews)} reviews fetched so far")
                    break

        logging.info(f"Successfully fetched {len(reviews)} reviews via GraphQL")
        return {
            'reviews': reviews,
            'total_reviews': len(reviews)
        }

    def scrape_reviews(self, url):
        """Scrape all reviews from a professor's RMP page using GraphQL API"""
        logging.info(f"Scraping reviews from: {url}")

        # Extract teacher ID and convert to GraphQL ID format
        teacher_id_encoded = self.extract_teacher_id_from_url(url)
        if not teacher_id_encoded:
            logging.error(f"Could not extract teacher ID from URL: {url}")
            return {'reviews': [], 'total_reviews': 0}

        # Fetch reviews using GraphQL with pagination
        return self.fetch_reviews_via_graphql(teacher_id_encoded)
            
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
                # Use the chat completions API
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an educational analyst summarizing professor reviews."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300
                )

                # Extract the text from the response
                if response.choices and len(response.choices) > 0:
                    choice = response.choices[0]
                    if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                        return choice.message.content

                # If we reach here, we couldn't extract text
                logging.error("Unable to parse text from OpenAI response object")
                return "Error generating analysis."
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
            df = pd.read_csv(os.path.join(OUTPUT_DIR, 'professors.csv'))
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
            with open(os.path.join(OUTPUT_DIR, 'professor_analyses.json'), 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
            # Also save as CSV
            analysis_df = pd.DataFrame(results)
            analysis_df.to_csv(os.path.join(OUTPUT_DIR, 'professor_analyses.csv'), index=False)
            logging.info("Successfully saved results to professor_analyses.json and professor_analyses.csv")
            
        except Exception as e:
            logging.error(f"Error processing professors: {e}")
            raise
            
    def close(self):
        """Clean up resources (no longer needed since we use GraphQL instead of Selenium)"""
        logging.info("Cleanup complete")

if __name__ == "__main__":
    scraper = ReviewScraper()
    try:
        scraper.process_all_professors()
    finally:
        scraper.close() 