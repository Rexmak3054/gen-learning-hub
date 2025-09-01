#!/bin/bash

echo "🧪 Testing the simplified backend locally..."
echo ""

# Navigate to the api directory
cd api

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🚀 Starting server..."
echo "Server will start on http://localhost:8000"
echo ""
echo "🔗 Test URLs:"
echo "  Health check: http://localhost:8000/api/health"
echo "  Test endpoint: http://localhost:8000/api/test"
echo "  Debug env: http://localhost:8000/api/debug/env"
echo ""
echo "📝 To test course search:"
echo 'curl -X POST http://localhost:8000/api/search-courses -H "Content-Type: application/json" -d "{\"query\": \"python programming\", \"k\": 5}"'
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================="

# Start the server
python index.py
