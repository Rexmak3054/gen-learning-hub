#!/bin/bash

echo "🔧 FIXING AJV DEPENDENCY CONFLICT"
echo "================================="
echo ""

cd frontend

echo "🗑️ Cleaning up node_modules and lock files..."
rm -rf node_modules
rm -f package-lock.json
rm -f yarn.lock

echo ""
echo "📦 Installing fresh dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo ""
    echo "🏗️ Testing build..."
    npm run build
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ BUILD SUCCESSFUL!"
        echo "🎉 Dependency conflict resolved!"
    else
        echo ""
        echo "❌ Build still failing, trying alternative fix..."
        echo "🔄 Installing compatible ajv version..."
        npm install ajv@^8.12.0 --save-dev
        npm run build
    fi
else
    echo ""
    echo "❌ npm install failed"
    echo "Trying alternative approach..."
fi
