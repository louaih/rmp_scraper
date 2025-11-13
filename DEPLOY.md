# RateMyProfessors Review Analyzer - Web App

A Flask-based web application for analyzing RateMyProfessors professor reviews using AI-powered insights.

## Features

- 🌐 Web-based interface (no CLI needed)
- 🔍 Analyzes professor reviews using OpenAI API
- 📊 Displays quality and difficulty ratings
- 📥 Export results as CSV
- 🐳 Docker support for easy CentOS deployment
- ⚡ GraphQL-based pagination to fetch all reviews
- 🔐 No authentication required

## Local Development

### Prerequisites

- Python 3.9+
- pip
- OPENAI_API_KEY environment variable

### Setup

1. **Clone and navigate to project:**
   ```bash
   cd rmp_scraper
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

5. **Run the app:**
   ```bash
   python app.py
   ```

6. **Open in browser:**
   ```
   http://localhost:5000
   ```

## Docker Deployment on CentOS

### Prerequisites

- Docker installed on your CentOS VPS
- Docker Compose installed
- OPENAI_API_KEY

### Quick Start

1. **Clone repository on your VPS:**
   ```bash
   git clone <your-repo-url>
   cd rmp_scraper
   ```

2. **Create .env file with your API key:**
   ```bash
   echo "OPENAI_API_KEY=sk-your-key-here" > .env
   ```

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Access the app:**
   ```
   http://your-vps-ip:5000
   ```

5. **View logs:**
   ```bash
   docker-compose logs -f rmp-analyzer
   ```

6. **Stop the app:**
   ```bash
   docker-compose down
   ```

### Manual Docker Build (if not using Compose)

```bash
# Build image
docker build -t rmp-analyzer .

# Run container
docker run -d \
  --name rmp-analyzer \
  -p 5000:5000 \
  -e OPENAI_API_KEY=sk-your-key-here \
  -v $(pwd)/data:/app/data \
  rmp-analyzer
```

## CentOS VPS Setup (Full Manual)

If you prefer not to use Docker:

### 1. Install Python 3.9

```bash
yum update -y
yum install centos-release-scl -y
yum install rh-python39 rh-python39-pip -y
echo 'source /opt/rh/rh-python39/enable' >> ~/.bashrc
source ~/.bashrc
```

### 2. Clone and Setup

```bash
cd /opt
git clone <your-repo-url> rmp_scraper
cd rmp_scraper
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create .env file

```bash
cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
EOF
```

### 4. Setup Systemd Service

Create `/etc/systemd/system/rmp-analyzer.service`:

```ini
[Unit]
Description=RateMyProfessors Review Analyzer
After=network.target

[Service]
Type=notify
User=nobody
WorkingDirectory=/opt/rmp_scraper
Environment="PATH=/opt/rmp_scraper/venv/bin"
ExecStart=/opt/rmp_scraper/venv/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --timeout 120 \
    app:app
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

### 5. Enable and Start Service

```bash
systemctl daemon-reload
systemctl enable rmp-analyzer
systemctl start rmp-analyzer
systemctl status rmp-analyzer
```

### 6. Setup Nginx Reverse Proxy (Optional)

Install Nginx:
```bash
yum install nginx -y
```

Create `/etc/nginx/conf.d/rmp-analyzer.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

Enable and start Nginx:
```bash
systemctl enable nginx
systemctl start nginx
```

## Usage

1. **Open web interface** at `http://your-vps-ip:5000`

2. **Paste RateMyProfessors URLs** (one per line):
   ```
   https://www.ratemyprofessors.com/professor/148929
   https://www.ratemyprofessors.com/professor/234567
   ```

3. **Click "Analyze"** and wait for results

4. **View results** with quality/difficulty ratings and AI analysis

5. **Export as CSV** for further analysis

## API Endpoints

### POST /api/analyze
Analyze professor reviews

**Request:**
```json
{
  "professor_urls": [
    "https://www.ratemyprofessors.com/professor/148929",
    "https://www.ratemyprofessors.com/professor/234567"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "url": "...",
      "professor_name": "...",
      "number_of_reviews": 42,
      "average_quality": 4.2,
      "average_difficulty": 3.5,
      "analysis": "AI-generated summary...",
      "status": "success"
    }
  ],
  "total_professors": 2,
  "successful_analyses": 2
}
```

### POST /api/export
Export results as CSV

**Request:**
```json
{
  "results": [...] // results array from /api/analyze
}
```

### GET /api/health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "message": "Service is running"
}
```

## Troubleshooting

### 403 Forbidden Error
The app includes proper browser headers to avoid being blocked. If you still get 403:
- Wait a few minutes and retry
- Check your OPENAI_API_KEY is valid

### Rate Limiting
If you hit OpenAI rate limits:
- The app has built-in exponential backoff
- Wait a few seconds and retry
- Consider upgrading your OpenAI plan

### Docker Issues on CentOS 7
- If Docker is not installed: `yum install docker-io`
- Make sure Docker daemon is running: `systemctl start docker`
- Add user to docker group: `usermod -aG docker $USER`

## Performance

- Reviews are fetched via GraphQL with cursor-based pagination
- Processes up to 20 reviews per API request
- AI analysis uses gpt-3.5-turbo model
- Typical analysis time: 5-15 seconds per professor

## License

MIT

## Support

For issues or questions, check the logs:

**Docker:**
```bash
docker-compose logs rmp-analyzer
```

**Systemd:**
```bash
journalctl -u rmp-analyzer -f
```

## Production Considerations

1. **SSL/TLS**: Use Let's Encrypt with Nginx for HTTPS
2. **Rate Limiting**: Consider adding rate limiting middleware for API
3. **Caching**: Could cache professor data to reduce API calls
4. **Database**: Could store results in PostgreSQL for historical tracking
5. **Queue**: For large batches, consider Celery for async processing
