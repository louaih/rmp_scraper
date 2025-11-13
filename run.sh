#!/bin/bash

# RMP Analyzer Web App - Local Startup Script

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file not found!"
    echo "Please create a .env file with your OPENAI_API_KEY:"
    echo ""
    echo "  cp .env.example .env"
    echo "  # Edit .env and add your key"
    echo ""
    exit 1
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "OPENAI_API_KEY" .env || grep "OPENAI_API_KEY=sk-your-api-key-here" .env > /dev/null; then
    echo "⚠️  OPENAI_API_KEY not properly configured in .env"
    exit 1
fi

# Create data directories if they don't exist
mkdir -p data/input data/output logs

# Start the Flask app
echo ""
echo "🚀 Starting RMP Analyzer Web App..."
echo "📍 Access at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python app.py
