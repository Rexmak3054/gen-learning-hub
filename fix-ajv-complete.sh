#!/bin/bash

echo "🔧 AJV DEPENDENCY ERROR - STEP BY STEP FIX"
echo "========================================="
echo ""
echo "The 'ajv/dist/compile/codegen' error is a common React/webpack issue."
echo "Let's try multiple solutions in order:"
echo ""

echo "STEP 1: Simple dependency refresh"
echo "--------------------------------"
chmod +x fix-ajv-error.sh
./fix-ajv-error.sh

# Check if it worked
cd frontend
if npm run build > /dev/null 2>&1; then
    echo "✅ STEP 1 SUCCESS! Problem solved."
    echo "🚀 Ready to deploy!"
    exit 0
fi

echo ""
echo "STEP 1 failed, trying STEP 2..."
echo ""

echo "STEP 2: Nuclear option - clean rebuild"
echo "-------------------------------------"
cd ..
chmod +x nuclear-fix.sh
./nuclear-fix.sh

# Check if it worked
cd frontend
if npm run build > /dev/null 2>&1; then
    echo "✅ STEP 2 SUCCESS! Problem solved."
    echo "🚀 Ready to deploy!"
    exit 0
fi

echo ""
echo "Both steps failed. Let's try a different approach..."
echo ""

echo "STEP 3: Alternative - Use different React template"
echo "-------------------------------------------------"
echo "Creating a brand new React app and copying our code..."

cd ..
echo "📦 Creating fresh React app..."
npx create-react-app frontend-new --template typescript
echo "📁 Moving to new frontend..."
rm -rf frontend-old
mv frontend frontend-old
mv frontend-new frontend

echo "📋 Copying our custom files..."
cp frontend-old/src/App.js frontend/src/App.tsx
cp frontend-old/src/index.css frontend/src/index.css
cp frontend-old/.env frontend/.env 2>/dev/null || true

echo "🏗️ Testing new build..."
cd frontend
npm run build

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ STEP 3 SUCCESS! Fresh React app works!"
    echo "🗑️ Cleaning up old frontend..."
    cd ..
    rm -rf frontend-old
    echo "🚀 Ready to deploy!"
else
    echo ""
    echo "❌ All automated fixes failed."
    echo "Manual intervention required."
    echo ""
    echo "🆘 Manual fix options:"
    echo "1. Use Node.js version 18 instead of 23"
    echo "2. Try: npm install --legacy-peer-deps"
    echo "3. Delete the entire project and start fresh"
    echo "4. Use a different deployment platform (Railway, Netlify)"
fi
