#!/bin/bash

# Fix dependency conflicts script

echo "🔧 Fixing dependency conflicts..."

# Remove existing venv to start fresh
if [ -d "venv" ]; then
    echo "🗑️  Removing existing virtual environment..."
    rm -rf venv
fi

# Create fresh virtual environment
echo "📦 Creating fresh virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip first
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies one by one to catch conflicts
echo "📚 Installing core dependencies..."
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install python-dotenv==1.0.0
pip install "pydantic>=1.10.0,<2.0.0"

echo "📚 Installing your existing dependencies..."
pip install mcp
pip install requests
pip install beautifulsoup4
pip install boto3
pip install opensearch-py

echo "📚 Installing LangChain dependencies..."
pip install langchain
pip install langchain-core  
pip install langchain-openai
pip install langgraph

# Try to install MCP adapters last
echo "📚 Installing MCP adapters..."
pip install langchain-mcp-adapters

echo "✅ Dependencies installed. Testing import..."

# Test the imports
python -c "
try:
    from fastapi import FastAPI
    from pydantic import BaseModel
    from langchain_core.messages import HumanMessage
    print('✅ All core imports successful!')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

echo "🎉 Dependency fix completed!"
echo "Now try: python main.py"
