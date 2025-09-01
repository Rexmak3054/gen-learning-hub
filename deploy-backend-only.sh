#!/bin/bash

echo "🚀 DEPLOY BACKEND ONLY - BYPASS FRONTEND ISSUES"
echo "=============================================="
echo ""
echo "If frontend keeps failing, let's deploy just the backend first"
echo "to verify the API works, then fix frontend separately."
echo ""

echo "📁 Backing up current vercel.json..."
cp vercel.json vercel-fullstack.json

echo "📝 Using backend-only configuration..."
cp vercel-backend-only.json vercel.json

echo ""
echo "✅ Ready to deploy backend only!"
echo ""
echo "Next steps:"
echo "1. git add ."
echo "2. git commit -m 'Deploy: Backend only to bypass frontend build issues'"  
echo "3. git push origin main"
echo "4. Test your API: https://your-app.vercel.app/api/health"
echo ""
echo "After backend works, we'll fix frontend separately."
echo ""
echo "Deploy backend only now? (y/n)"

read -p "" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add .
    git commit -m "Deploy: Backend only to bypass frontend build issues"
    git push origin main
    echo ""
    echo "🚀 Backend deployment pushed!"
    echo "Check Vercel dashboard for deployment status."
    echo ""
    echo "Test endpoints after deployment:"
    echo "• https://your-app.vercel.app/api/health"
    echo "• https://your-app.vercel.app/api/test"
    echo "• https://your-app.vercel.app/api/debug/env"
else
    echo "Deployment cancelled. Try the frontend fixes instead."
    echo "Restoring original vercel.json..."
    cp vercel-fullstack.json vercel.json
fi
