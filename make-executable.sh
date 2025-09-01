#!/bin/bash

echo "🔧 Making scripts executable..."
chmod +x setup-git.sh
chmod +x test-api-local.sh  
chmod +x deploy-guide.sh

echo "✅ Scripts are now executable!"
echo ""
echo "📋 Available commands:"
echo "  ./deploy-guide.sh     - Show complete deployment guide"
echo "  ./setup-git.sh        - Initialize Git repository"
echo "  ./test-api-local.sh   - Test backend locally"
echo ""
echo "🚀 Start with: ./deploy-guide.sh"
