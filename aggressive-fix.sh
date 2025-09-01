#!/bin/bash

echo "🔧 AGGRESSIVE AJV KEYWORDS FIX"
echo "============================="
echo ""
echo "This is a deeper dependency conflict. Let's fix it with npm overrides."
echo ""

cd frontend

echo "🗑️ Complete cleanup..."
rm -rf node_modules package-lock.json yarn.lock

echo ""
echo "📝 Creating package.json with aggressive dependency overrides..."
cat > package.json << 'EOF'
{
  "name": "grace-papers-gen-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "react-scripts": "5.0.1",
    "lucide-react": "^0.263.1",
    "web-vitals": "^3.5.2"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "GENERATE_SOURCEMAP=false react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "overrides": {
    "ajv": "8.12.0",
    "ajv-keywords": "5.1.0",
    "schema-utils": "3.3.0"
  },
  "resolutions": {
    "ajv": "8.12.0",
    "ajv-keywords": "5.1.0"
  },
  "devDependencies": {
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32", 
    "tailwindcss": "^3.4.0"
  }
}
EOF

echo ""
echo "🔄 Installing with legacy peer deps flag..."
npm install --legacy-peer-deps

echo ""
echo "🏗️ Testing build..."
npm run build

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Aggressive fix worked!"
    echo "🎉 Build completed successfully"
else
    echo ""
    echo "❌ Still failing. Let's try the ultimate nuclear option..."
    echo "🚨 This will use an older React Scripts version that's more stable"
    echo ""
    
    cat > package.json << 'EOF'
{
  "name": "grace-papers-gen-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "react-scripts": "4.0.3",
    "lucide-react": "^0.263.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF

    echo "📦 Installing with older, stable React Scripts..."
    rm -rf node_modules package-lock.json
    npm install --legacy-peer-deps
    
    echo ""
    echo "🏗️ Testing with React Scripts 4.0.3..."
    npm run build
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ SUCCESS! Older React Scripts worked!"
        echo "🎉 Sometimes older is better for stability"
    else
        echo ""
        echo "❌ Even the nuclear option failed."
        echo "This suggests a Node.js version incompatibility."
        echo ""
        echo "🔄 Final recommendation: Use Node.js 16 or 18"
        echo "Your current Node version might be too new."
        echo ""
        echo "If you have nvm:"
        echo "  nvm install 18"
        echo "  nvm use 18" 
        echo "  npm install"
        echo "  npm run build"
    fi
fi
