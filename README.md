# RateMyProfessor Course Scraper

This tool scrapes RateMyProfessor.com to find ratings for professors teaching specific NYU courses.

## Prerequisites

- Python 3.7+
- Brave browser installed (default installation path: C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe)
- pip (Python package installer)

## Installation

1. Clone this repository or download the files
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Simply run the scraper script:
```bash
python scraper.py
```

The script will:
1. Search for professors teaching each course
2. Collect their ratings and department information
3. Save the results to `professor_ratings.csv`

## Output

The script generates a CSV file with the following columns:
- course_code: The course code (e.g., "ANTH-UA 326")
- course_name: The name of the course
- professor_name: Name of the professor
- department: Department the professor belongs to
- rating: The professor's rating on RateMyProfessor

## Note

- The script uses Selenium with Brave browser to automate the scraping process
- If your Brave browser is installed in a different location, you'll need to update the path in `scraper.py`
- It includes a 2-second delay between requests to be respectful to the RateMyProfessor servers
- Only the first 5 professor results per course are collected to keep the search focused
- Make sure you have a stable internet connection while running the script 