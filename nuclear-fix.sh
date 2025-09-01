#!/bin/bash

echo "🚨 NUCLEAR OPTION: Complete Clean Build"
echo "======================================"
echo ""
echo "This will completely recreate your frontend with minimal dependencies"
echo "to guarantee Vercel deployment success."
echo ""

read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Aborted."
    exit 1
fi

cd frontend

echo "🗑️ Complete cleanup..."
rm -rf node_modules
rm -f package-lock.json
rm -f yarn.lock

echo ""
echo "📦 Creating minimal package.json..."
cat > package.json << 'EOF'
{
  "name": "grace-papers-gen-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "react-scripts": "5.0.1"
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

echo ""
echo "🔄 Fresh install with exact versions..."
npm install

echo ""
echo "🏗️ Testing build..."
npm run build

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Clean build completed"
    echo "🎉 Ready for Vercel deployment"
    echo ""
    echo "📊 Build info:"
    ls -la build/
    du -sh build/
    echo ""
    echo "🚀 Next steps:"
    echo "1. git add ."
    echo "2. git commit -m 'Fix: Nuclear option - clean minimal build'"
    echo "3. git push origin main"
    echo "4. Vercel will auto-deploy successfully!"
else
    echo ""
    echo "❌ Still failing. This indicates a deeper system issue."
    echo "Try deleting the entire frontend folder and recreating it."
fi
