#!/bin/bash

echo "🚀 Starting backend server for debugging..."

# Navigate to backend directory
cd /Users/hiufungmak/grace-papers-gen/backend

# Start the server with detailed logging
echo "📝 Starting server with enhanced logging..."
python main_with_agent.py

# Keep it running
echo "✅ Server started. Check the logs above for debugging information."
echo "💡 In another terminal, run:"
echo "   cd /Users/hiufungmak/grace-papers-gen/debug"
echo "   python test_agent.py"
