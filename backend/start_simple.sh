#!/bin/bash

# Simple start script that works with your existing environment

echo "🚀 Starting Grace Papers FastAPI Backend (Compatible Mode)..."

# Don't create a new venv - use your existing environment
echo "🔧 Using existing Python environment..."

# Check versions first
echo "🔍 Checking package compatibility..."
python check_versions.py

echo ""
echo "📚 Installing only missing dependencies..."

# Install only FastAPI and uvicorn with compatible versions
pip install fastapi==0.68.2 uvicorn==0.15.0

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Please copy .env.example to .env and configure your environment variables."
    cp .env.example .env
    echo "📄 Created .env file from template. Please edit it with your actual values."
fi

# Start the FastAPI application
echo "🌟 Starting FastAPI application on port 8000..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🔍 Alternative docs at: http://localhost:8000/redoc" 
echo "❤️  Health check at: http://localhost:8000/health"
echo ""

python main.py
