import os
from dotenv import load_dotenv
import requests
import time
import pandas as pd
import json

# Get the project root directory (two levels up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(PROJECT_ROOT, 'data', 'input')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'data', 'output')

class RMPScraper:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

    def format_course_code(self, code):
        # Convert "ANTH-UA 326" to "ANTH326"
        return code.split('-')[0] + code.split()[-1]

    def google_search(self, course_code):
        no_space_code = "".join(course_code.split())
        foo = course_code.split('-')
        no_hyphen_code = foo[0] + "".join(foo[1:])
        no_space_no_hyphen_code = foo[0]+"".join(foo[1].split())
        no_space_no_hyphen_no_ua_code = foo[0] + course_code.split()[-1]
        # TODO: Remove hardcoded NYU
        query = f'site:ratemyprofessors.com ("{course_code}" OR "{no_space_code}" OR "{no_hyphen_code}" OR "{no_space_no_hyphen_code}" OR "{no_space_no_hyphen_no_ua_code}") ("NYU" OR "New York University")'
        print(query)
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': 10
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making Google search request: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")
            return None

    def scrape_course(self, course_code, course_name):
        print(f"\nSearching for professors teaching {course_code}...")
        
        search_results = self.google_search(course_code)
        if not search_results or 'items' not in search_results:
            print(f"No results found for {course_code}")
            return []
        
        professors = []
        for item in search_results['items']:
            if '/professor/' in item['link']:
                professors.append({
                    'course_code': course_code,
                    'course_name': course_name,
                    'professor_name': item['title'],
                    'url': item['link']
                })
        return professors

    def filter_nyu_professors(self, results):
        """
        Filter out non-NYU professors from the results
        """
        nyu_professors = []
        for prof in results:
            if "NYU" in prof['professor_name'] or "New York University" in prof['professor_name']:
                nyu_professors.append(prof)
            else:
                print(f"Skipping non-NYU professor: {prof['professor_name']}")
        
        return nyu_professors

    def scrape_all_courses(self):
        all_results = []
        
        # Read courses from input file
        courses_file = os.path.join(INPUT_DIR, 'courses.txt')
        with open(courses_file, 'r') as f:
            courses = {line.strip(): f"Course {line.strip()}" for line in f if line.strip()}
        
        for code, name in courses.items():
            results = self.scrape_course(code, name)
            # Filter for NYU professors only and clean up professor names
            nyu_results = self.filter_nyu_professors(results)
            for prof in nyu_results:
                name_parts = prof['professor_name'].split()
                prof['professor_name'] = f"{name_parts[0]} {name_parts[1]}"
            all_results.extend(nyu_results)
            
            # Save after each course in case of interruption
            df = pd.DataFrame(all_results)
            df.to_csv(os.path.join(OUTPUT_DIR, 'professors.csv'), index=False)
            
            time.sleep(3)  # Delay between courses
        
        print("\nFinal results saved to professors.csv")
        
        # Also save as JSON for better readability
        with open(os.path.join(OUTPUT_DIR, 'professors.json'), 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print("Detailed results saved to professors.json")

if __name__ == "__main__":
    scraper = RMPScraper()
    scraper.scrape_all_courses() 