#!/bin/bash

# Grace Papers FastAPI Backend Startup Script

echo "🚀 Starting Grace Papers FastAPI Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Please copy .env.example to .env and configure your environment variables."
    cp .env.example .env
    echo "📄 Created .env file from template. Please edit it with your actual values."
fi

# Start the FastAPI application with uvicorn
echo "🌟 Starting FastAPI application on port 8000..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🔍 Alternative docs at: http://localhost:8000/redoc"
echo "❤️  Health check at: http://localhost:8000/health"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info
