#!/bin/bash

echo "🧪 Testing Frontend Build Locally"
echo "================================"
echo ""

cd frontend

echo "📦 Installing dependencies..."
npm install

echo ""
echo "🏗️ Testing build process..."
npm run build

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ BUILD SUCCESSFUL!"
    echo "🎉 Frontend is ready for Vercel deployment"
    echo ""
    echo "🔍 Build output:"
    ls -la build/
    echo ""
    echo "📊 Build size:"
    du -sh build/
    echo ""
    echo "🚀 Ready to deploy to Vercel!"
else
    echo ""
    echo "❌ BUILD FAILED"
    echo "Check the error messages above for details"
    exit 1
fi
