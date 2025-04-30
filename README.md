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
   - Check console for logs and troubleshooting information

## Sample Output

### Professor Finder Output (professor_ratings.json)
```json
[
  {
    "course_code": "CS-UY 2124",
    "course_name": "Course CS-UY 2124",
    "professor_name": "John Sterling at NYU Tandon School of Engineering",
    "department": "Computer Science department at NYU...",
    "url": "https://www.ratemyprofessors.com/professor/125789"
  },
  {
    "course_code": "CS-UY 2124",
    "course_name": "Course CS-UY 2124",
    "professor_name": "Eugene Callahan at NYU Tandon School of Engineering",
    "department": "Computer Science department at NYU...",
    "url": "https://www.ratemyprofessors.com/professor/2220934"
  }
]
```

### Review Analyzer Output (course_professor_analyses.json)
```json
[
  {
    "course_code": "CS-UY 2124",
    "professor_name": "John Sterling",
    "number_of_reviews": 20,
    "average_quality": 3.3,
    "average_difficulty": 4.3,
    "analysis": "The professor, Sterling, receives mixed feedback from students. While many appreciate his deep knowledge and effective teaching style, there are recurring concerns about his rudeness and strict grading policies. Students feel that participating and asking questions are crucial to succeeding in his class, but they also mention feeling intimidated and disrespected at times. The difficulty of the course is consistently noted, with exams heavily weighted and minor errors resulting in significant point deductions. Some students find his teaching methods outdated, while others appreciate his dedication to teaching C++ and OOP concepts. Overall, opinions vary on Professor Sterling, with some students praising his expertise and others criticizing his interpersonal skills and grading approach. Students are advised to prepare thoroughly and actively engage to succeed in his challenging class."
  }
]
```

## Output Format

The tool generates two output files:
- `course_professor_analyses.json`
- `course_professor_analyses.csv`

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
