# RateMyProfessors Review Analyzer - Web App

A modern web application for analyzing RateMyProfessors professor reviews using AI-powered insights. Built with Flask and OpenAI API, it provides comprehensive analysis of teaching quality and student feedback.

## Quick Start

### Local Development (Windows/Mac/Linux)

```bash
# Clone and navigate
cd rmp_scraper

# Run the startup script
# On Windows:
run.bat

# On Mac/Linux:
chmod +x run.sh
./run.sh
```

Then open **http://localhost:5000** in your browser.

### Docker on CentOS VPS

```bash
# Set up your API key
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Run with Docker Compose
docker-compose up -d

# Access at http://your-vps-ip:5000
```

See [DEPLOY.md](DEPLOY.md) for comprehensive deployment guides.

## Features

- 🌐 **Web Interface** - No CLI needed, just paste URLs
- 🤖 **AI Analysis** - OpenAI-powered review summaries
- 📊 **Quality Metrics** - Displays quality and difficulty ratings
- 📥 **Export** - Download results as CSV
- 🐳 **Docker Ready** - Easy CentOS VPS deployment
- ⚡ **Full Pagination** - Fetches all reviews (not just first 5)
- 🔐 **No Auth Required** - Simple public interface

## Project Structure

```
rmp_scraper/
├── app.py                         # Flask application
├── templates/
│   └── index.html                # Web UI
├── src/
│   ├── professor_finder.py       # Professor search
│   └── review_analyzer.py        # Review analysis (GraphQL API)
├── data/                          # Data files
│   ├── input/
│   └── output/
├── Dockerfile                     # Docker image for CentOS
├── docker-compose.yml            # Docker Compose config
├── requirements.txt              # Python dependencies
├── DEPLOY.md                     # Deployment guide
├── run.sh                        # Linux/Mac startup
├── run.bat                       # Windows startup
└── README.md                     # This file
```

## How to Use

1. **Open the web app** at `http://localhost:5000` (local) or `http://your-vps-ip:5000` (VPS)

2. **Paste RateMyProfessors URLs** (one per line):
   ```
   https://www.ratemyprofessors.com/professor/148929
   https://www.ratemyprofessors.com/professor/234567
   ```

3. **Click Analyze** and wait for results (5-15 seconds per professor)

4. **View insights**:
   - Number of reviews
   - Quality rating (1-5)
   - Difficulty rating (1-5)
   - AI-generated summary

5. **Export as CSV** for further analysis

## What's Under the Hood

- **Web Framework**: Flask
- **API**: RateMyProfessors GraphQL with cursor-based pagination
- **AI Model**: OpenAI GPT-3.5-Turbo
- **Server**: Gunicorn (production)
- **Container**: CentOS 7 + Docker

### How It Works

1. User pastes professor URLs
2. App extracts teacher IDs and encodes them
3. Fetches all reviews via GraphQL (with pagination)
4. Sends reviews to OpenAI for analysis
5. Displays results with metrics
6. Allows export to CSV

## API Endpoints

All endpoints are JSON-based:

### POST /api/analyze
Analyze one or more professors

### POST /api/export
Export results as CSV

### GET /api/health
Health check

See [DEPLOY.md](DEPLOY.md#api-endpoints) for full API documentation.

## Requirements

- Python 3.9+
- OpenAI API key
- For VPS: Docker + Docker Compose (optional but recommended)

## Setup

### Local

```bash
pip install -r requirements.txt
echo "OPENAI_API_KEY=sk-your-key-here" > .env
python app.py
```

### Docker on CentOS

```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
docker-compose up -d
```

See [DEPLOY.md](DEPLOY.md) for detailed CentOS setup, Nginx reverse proxy, and systemd service options.

## Troubleshooting

**403 Forbidden?**
- The app includes proper browser headers. Wait a few minutes and retry.

**Rate Limited?**
- OpenAI rate limits apply. Built-in exponential backoff should handle it.

**Docker issues on CentOS 7?**
- Ensure Docker is running: `systemctl start docker`
- See [DEPLOY.md#docker-issues-on-centos-7](DEPLOY.md#docker-issues-on-centos-7)

## Performance

- Fetches all available reviews (not just first 5)
- Up to 20 reviews per GraphQL request
- AI analysis time: 5-15 seconds per professor
- Suitable for analyzing 50+ professors at once

## Production Deployment

For production on CentOS VPS:

1. **Use Docker** (simplest): See [DEPLOY.md](DEPLOY.md#docker-deployment-on-centos)
2. **Use Systemd** (manual): See [DEPLOY.md](DEPLOY.md#centos-vps-setup-full-manual)
3. **Add Nginx reverse proxy**: See [DEPLOY.md](DEPLOY.md#6-setup-nginx-reverse-proxy-optional)
4. **Add SSL/TLS**: Use Let's Encrypt with Nginx

See [DEPLOY.md](DEPLOY.md) for comprehensive production guides.

## License

MIT

## Support

For issues, check:
- Application logs: `docker-compose logs rmp-analyzer`
- System logs: `journalctl -u rmp-analyzer -f` (if using systemd)
- Health endpoint: `curl http://localhost:5000/api/health`
