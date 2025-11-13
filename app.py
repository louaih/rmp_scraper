"""
Flask web app for RateMyProfessors review analysis
"""
import os
import json
import logging
from flask import Flask, render_template, request, jsonify, send_file
from io import StringIO
import csv
from src.review_analyzer import ReviewScraper
from src.professor_finder import RMPScraper
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global instances
scraper = None
finder = None

def get_scraper():
    """Get or create a scraper instance"""
    global scraper
    if scraper is None:
        try:
            scraper = ReviewScraper()
        except Exception as e:
            logger.error(f"Failed to initialize scraper: {e}")
            raise
    return scraper

def get_finder():
    """Get or create a professor finder instance"""
    global finder
    if finder is None:
        try:
            finder = RMPScraper()
        except Exception as e:
            logger.error(f"Failed to initialize professor finder: {e}")
            # Finder is optional (requires Google Search API keys)
            return None
    return finder


@app.route('/', methods=['GET'])
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/api/search-professors', methods=['POST'])
def search_professors():
    """Search for professors teaching a course"""
    try:
        data = request.get_json()
        if not data or 'course_codes' not in data:
            return jsonify({'error': 'Missing course_codes in request'}), 400

        course_codes = data.get('course_codes', [])
        if not isinstance(course_codes, list) or len(course_codes) == 0:
            return jsonify({'error': 'course_codes must be a non-empty list'}), 400

        finder = get_finder()
        if finder is None:
            return jsonify({
                'error': 'Professor finder not available. Set GOOGLE_CLOUD_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables.',
                'professors': []
            }), 503

        results = []
        for course_code in course_codes:
            logger.info(f"Searching for professors teaching {course_code}")
            try:
                professors = finder.scrape_course(course_code, f"Course {course_code}")
                results.extend(professors)
                logger.info(f"Found {len(professors)} professors for {course_code}")
            except Exception as e:
                logger.error(f"Error searching for {course_code}: {e}")

        return jsonify({
            'success': True,
            'professors': results,
            'total_professors': len(results)
        })

    except Exception as e:
        logger.error(f"Error in /api/search-professors: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API endpoint to analyze professor reviews"""
    try:
        data = request.get_json()
        
        # Support both URLs and professor names
        professor_urls = data.get('professor_urls', [])
        professor_names = data.get('professor_names', [])
        
        if not professor_urls and not professor_names:
            return jsonify({'error': 'Missing professor_urls or professor_names in request'}), 400

        # If professor names provided, convert to URLs via search
        if professor_names and not professor_urls:
            finder = get_finder()
            if finder is None:
                # Try to search using the RateMyProfessors URL pattern directly
                logger.info("Attempting to search for professors by name")
                professor_urls = []
                for name in professor_names:
                    # This is a fallback - in production you'd want proper name-to-URL mapping
                    logger.warning(f"Cannot convert professor name to URL without Google Search API: {name}")
            else:
                professor_urls = []
                for name in professor_names:
                    # Search for this professor name
                    try:
                        # We'd need to implement a name-based search in RMPScraper
                        logger.info(f"Searching for professor: {name}")
                    except Exception as e:
                        logger.error(f"Error searching for professor {name}: {e}")

        if not professor_urls:
            return jsonify({'error': 'No professor URLs found'}), 400

        scraper = get_scraper()
        results = []

        for url in professor_urls:
            logger.info(f"Processing professor URL: {url}")
            try:
                # Scrape reviews
                review_data = scraper.scrape_reviews(url)

                if review_data and review_data['reviews']:
                    # Calculate averages
                    quality_ratings = [r['quality_rating'] for r in review_data['reviews'] if r['quality_rating'] is not None]
                    difficulty_ratings = [r['difficulty_rating'] for r in review_data['reviews'] if r['difficulty_rating'] is not None]

                    avg_quality = sum(quality_ratings) / len(quality_ratings) if quality_ratings else None
                    avg_difficulty = sum(difficulty_ratings) / len(difficulty_ratings) if difficulty_ratings else None

                    # Get analysis
                    analysis = scraper.analyze_reviews(review_data['reviews'])

                    results.append({
                        'url': url,
                        'professor_name': 'Professor',
                        'number_of_reviews': len(review_data['reviews']),
                        'average_quality': avg_quality,
                        'average_difficulty': avg_difficulty,
                        'analysis': analysis,
                        'status': 'success'
                    })
                    logger.info(f"Successfully analyzed {len(review_data['reviews'])} reviews for {url}")
                else:
                    results.append({
                        'url': url,
                        'status': 'error',
                        'message': 'No reviews found for this professor'
                    })
                    logger.warning(f"No reviews found for {url}")

            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
                results.append({
                    'url': url,
                    'status': 'error',
                    'message': str(e)
                })

        return jsonify({
            'success': True,
            'results': results,
            'total_professors': len(professor_urls),
            'successful_analyses': len([r for r in results if r.get('status') == 'success'])
        })

    except Exception as e:
        logger.error(f"Error in /api/analyze: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export', methods=['POST'])
def export_results():
    """Export results as CSV"""
    try:
        data = request.get_json()
        results = data.get('results', [])

        if not results:
            return jsonify({'error': 'No results to export'}), 400

        # Create CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=['url', 'professor_name', 'number_of_reviews', 'average_quality', 'average_difficulty', 'analysis'])
        writer.writeheader()

        for result in results:
            if result.get('status') == 'success':
                writer.writerow({
                    'url': result.get('url', ''),
                    'professor_name': result.get('professor_name', ''),
                    'number_of_reviews': result.get('number_of_reviews', ''),
                    'average_quality': result.get('average_quality', ''),
                    'average_difficulty': result.get('average_difficulty', ''),
                    'analysis': result.get('analysis', '')
                })

        # Return CSV file
        output.seek(0)
        return send_file(
            StringIO(output.getvalue()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='professor_analyses.csv'
        )

    except Exception as e:
        logger.error(f"Error in /api/export: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Try to get scraper to verify OpenAI connection
        scraper = get_scraper()
        return jsonify({'status': 'healthy', 'message': 'Service is running'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'message': str(e)}), 503


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Run on 0.0.0.0 to allow external connections
    app.run(host='0.0.0.0', port=5000, debug=False)
