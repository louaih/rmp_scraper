# RateMyProfessor Course Scraper

This tool uses Google Custom Search API to find RateMyProfessor.com ratings for professors teaching specific NYU courses.

## Prerequisites

- Python 3.7+
- Google Cloud API key
- Google Custom Search Engine ID
- pip (Python package installer)

## Installation

1. Clone this repository or download the files
2. Install the required packages:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file in the project root with your API credentials:
```
GOOGLE_CLOUD_API_KEY=your_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

## Usage

Simply run the scraper script:
```bash
python scraper.py
```

The script will:
1. Search for professors teaching each course using Google Custom Search API
2. Filter results to only include NYU professors
3. Save the results to both `professor_ratings.csv` and `professor_ratings.json`

## Output

The script generates two files:
1. `professor_ratings.csv` with the following columns:
   - course_code: The course code (e.g., "ANTH-UA 326")
   - course_name: The name of the course
   - professor_name: Name of the professor
   - department: Department the professor belongs to
   - url: Link to the professor's RateMyProfessor page

2. `professor_ratings.json` containing the same data in JSON format for better readability

## Note

- The script uses Google Custom Search API to find relevant RateMyProfessor pages
- It includes a 3-second delay between course searches to respect API rate limits
- Results are filtered to only include NYU professors
- Make sure you have a stable internet connection while running the script
- The script saves progress after each course in case of interruption 