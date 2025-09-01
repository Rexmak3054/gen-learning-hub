#!/bin/bash

echo "🚀 Starting Clean Grace Papers Chat Agent..."
echo "📍 Available endpoints:"
echo "   - Health: http://localhost:8001/health"
echo "   - Clean Demo: http://localhost:8001/demo-clean"
echo "   - API: http://localhost:8001/api/chat/*"
echo ""

# Change to backend directory
cd "$(dirname "$0")"

# Start the clean agent
echo "🌊 Starting clean agent chat server..."
python clean_agent_chat.py