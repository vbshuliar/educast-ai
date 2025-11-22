#!/bin/bash

echo "================================================"
echo "  EduCast AI - Starting Application"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "   Please copy .env.example to .env and add your API keys"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if API key is set
if ! grep -q "VALYU_API_KEY=.*[^_]" .env; then
    echo "⚠️  Warning: VALYU_API_KEY not set in .env file"
    echo ""
fi

echo "✓ Starting Flask API server on http://localhost:5001"
echo "✓ Open frontend at: frontend/index.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the API server
python3 api.py
