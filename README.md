# RateMyProfessors Scraper & Analyzer [profs.louai.dev](https://profs.louai.dev)

## Deployed on [Vercel](https://profs.louai.dev)

Rate and summarize RateMyProfessors data for NYU courses. This project bundles a Flask web app with a command-line workflow that discovers professors teaching a set of courses, fetches their reviews through RateMyProfessors' GraphQL API, and generates AI-powered summaries with OpenAI.

## Features
- Discover RateMyProfessors profile links for NYU courses via Google Custom Search.
- Scrape complete review histories using authenticated GraphQL requests.
- Summarize sentiment, strengths, and pain points with OpenAI GPT models.
- Export structured CSV/JSON outputs for downstream analysis.
- Web UI with Google OAuth login restricted to `nyu.edu` accounts.
- Docker and Vercel deployment artifacts plus PowerShell/Bash helpers.

## Project Layout
```
├─ app.py                  # Flask entrypoint for the authenticated web app
├─ main.py                 # CLI orchestration pipeline for batch scraping + analysis
├─ src/
│  ├─ auth.py              # Google OAuth helpers and access control
│  ├─ professor_finder.py  # Google Custom Search integration for RMP profiles
│  └─ review_analyzer.py   # Review scraping + OpenAI summarization
├─ data/
│  ├─ input/courses.txt            # Course codes to seed professor discovery
│  └─ output/…                     # Generated CSV/JSON artifacts
├─ templates/                # Jinja templates for the Flask UI
├─ requirements.txt          # Python dependencies
├─ Dockerfile, docker-compose.yml
├─ run.sh, run.bat           # Convenience launch scripts
└─ DEPLOY.md                 # Extended deployment guidance
```

## Prerequisites
- Python 3.9 or newer.
- An OpenAI API key with access to `gpt-3.5-turbo` (or compatible) models.
- Optional: Google Custom Search and Google OAuth credentials.
- Optional: Docker + Docker Compose for containerized runs.

## Quick Start (Local)
1. **Clone and enter the project directory.**
2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   ```
3. **Install dependencies.**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment variables.** Create a `.env` file in the project root:

   | Variable | Required | Description |
   | --- | --- | --- |
   | `OPENAI_API_KEY` | ✅ | Used to call OpenAI for review summaries. |
   | `GOOGLE_CLOUD_API_KEY` | ✅ for professor discovery | Google Custom Search API key. |
   | `GOOGLE_SEARCH_ENGINE_ID` | ✅ for professor discovery | Custom Search Engine ID targeting RateMyProfessors. |
   | `GOOGLE_CLIENT_ID` | ✅ for web login | OAuth client for NYU Google Workspace. |
   | `GOOGLE_CLIENT_SECRET` | ✅ for web login | OAuth client secret. |
   | `OAUTH_REDIRECT_URI` | ✅ for deployed web app | Public callback URL for Google OAuth. Flask will infer one for local dev if omitted. |
   | `SECRET_KEY` | ⚠️ recommended | Flask session secret. Random value generated if omitted. |

   Copy `data/input/courses.txt.example` to `data/input/courses.txt` and add the course codes you care about.

5. **Run the Flask app** (NYU-authenticated web UI):
   ```bash
   flask --app app run
   # or use run.sh / run.bat if you prefer
   ```
   Visit `http://127.0.0.1:5000` and authenticate with an `@nyu.edu` Google account.

### CLI Workflow
Use the pipeline in `main.py` when you want to run the full scrape/analyze/export sequence from a terminal.
```bash
python main.py ANTH-UA 326 MATH-UA 120     # explicit course codes
# or rely on data/input/courses.txt
python main.py
```
Results land in `data/output/` as both CSV and JSON files (`professors.*`, `course_professor_analyses.*`, etc.). A rolling log of operations is stored in `scraper.log`.

### Docker
The repository ships with container definitions for reproducible deployments.
```bash
docker compose up --build
```
Mount `data/` as a volume if you want to persist outputs. More production-focused steps (CentOS, systemd, Nginx) are documented in `DEPLOY.md`.

## Testing & Verification
- Ensure `OPENAI_API_KEY` is valid; initialization performs a lightweight smoke test.
- Confirm Google Custom Search configuration by checking the console output of `src/professor_finder.py` for constructed queries.
- Use the `/api/health` endpoint when the Flask app is running to verify connectivity.

## Contribution Guide
- **Workflow**: Fork → create a topic branch → open a pull request. Keep commits scoped and descriptive.
- **Environment**: Follow the setup steps above; run `pip install -r requirements.txt` inside your virtualenv.
- **Style**: Match existing Python conventions, prefer logging over prints, and document new environment variables in this README.
- **Testing**: Exercise both the CLI (`python main.py`) and key API endpoints (`/api/analyze`, `/api/export`) for regressions. Update or add sample data in `data/input/`/`data/output/` only when necessary.
- **Security**: Never commit secrets. Use `.env` locally and document any new keys or credentials that contributors must supply.
- **Docs**: Update `README.md`, `DEPLOY.md`, and in-line docstrings whenever you change setup steps, endpoints, or data formats.

Questions or enhancements? Open an issue or start a discussion on your fork before large structural changes.


