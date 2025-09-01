#!/bin/bash

echo "🚀 Initializing Git repository..."

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Grace Papers Gen - AI Learning Platform

- Frontend: React.js application
- Backend: FastAPI with course search functionality  
- Ready for Vercel deployment"

echo "✅ Initial commit created!"
echo ""
echo "🌐 Next steps:"
echo "1. Create a GitHub repository"
echo "2. Push your code: git remote add origin <your-repo-url>"
echo "3. git push -u origin main"
echo "4. Deploy to Vercel!"
