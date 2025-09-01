#!/bin/bash

echo "🚀 Starting Grace Papers Backend with Improved Streaming..."
echo "📍 Available endpoints:"
echo "   - Health: http://localhost:8000/health"
echo "   - Original Demo: http://localhost:8000/demo"
echo "   - Improved Demo: http://localhost:8000/demo-improved"
echo ""

# Change to backend directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Start the server
echo "🌊 Starting improved streaming server..."
python main_with_agent.py