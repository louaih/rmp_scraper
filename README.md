# Course Professor Review Analyzer

This tool helps students make informed decisions about their course selections by analyzing RateMyProfessors reviews for professors teaching specific courses. It provides a comprehensive overview of teaching quality, course difficulty, and student feedback for each professor.

## Features

- Scrapes reviews from RateMyProfessors for specified courses
- Analyzes teaching quality and course difficulty ratings
- Generates AI-powered summaries of student feedback
- Organizes results by course code for easy comparison
- Outputs results in both JSON and CSV formats

## Usage

1. **Setup**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Provide Course Codes**:
   You can specify courses in two ways:
   - Command line arguments:
     ```bash
     python main.py "CS-UY 2124" "CS-UY 1114"
     ```
   - Or create a `courses.txt` file with one course code per line:
     ```
     CS-UY 2124
     CS-UY 1114
     ```

3. **Run the Analyzer**:
   ```bash
   python main.py
   ```

4. **View Results**:
   - Open `course_professor_analyses.json` in VS Code (enable word wrap with Alt+Z)
   - Or view `course_professor_analyses.csv` in Excel/Google Sheets
   - Check `scraper.log` for detailed processing information

## Output Format

The tool generates two output files:
- `course_professor_analyses.json`: Detailed analysis with word-wrapped text
- `course_professor_analyses.csv`: Tabular format for easy sorting/filtering

Each analysis includes:
- Course code
- Professor name
- Number of reviews
- Average quality rating
- Average difficulty rating
- AI-generated summary of student feedback

## Requirements

- Python 3.8+
- Selenium
- OpenAI API key (for review analysis)
- Firefox browser (for web scraping)

## Notes

- The tool respects RateMyProfessors' rate limits
- Results are cached to avoid repeated scraping
- Analysis requires a valid OpenAI API key with available quota
- Word wrap in VS Code (Alt+Z) makes the JSON output more readable

## Project Structure

- `main.py`: Main script for processing courses
- `review_scraper.py`: Core scraping and analysis functionality
- `professor_ratings.csv`: Database of professor URLs
- `courses.txt`: Optional input file for course codes
- `requirements.txt`: Python dependencies 