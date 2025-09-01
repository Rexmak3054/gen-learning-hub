#!/bin/bash

echo "🧪 Quick Test - API Endpoints"
echo "============================="

API_URL="http://localhost:8000"

echo ""
echo "🔍 Testing Health Check..."
curl -s "${API_URL}/api/health" | python -m json.tool

echo ""
echo "🔍 Testing Basic Endpoint..."
curl -s "${API_URL}/api/test" | python -m json.tool

echo ""
echo "🔍 Testing Environment Debug..."
curl -s "${API_URL}/api/debug/env" | python -m json.tool

echo ""
echo "🔍 Testing Course Search..."
curl -s -X POST "${API_URL}/api/search-courses" \
  -H "Content-Type: application/json" \
  -d '{"query": "python programming", "k": 3}' | python -m json.tool

echo ""
echo "✅ All tests completed!"
echo ""
echo "🌐 Ready for Vercel deployment!"
