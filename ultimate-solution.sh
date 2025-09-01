#!/bin/bash

echo "🚨 ULTIMATE SOLUTION: Deploy Backend Only + Simple Frontend"
echo "========================================================="
echo ""
echo "The frontend build issues are likely due to Node.js v23 incompatibility."
echo "Let's deploy a working solution RIGHT NOW, then fix frontend later."
echo ""

echo "OPTION 1: Deploy backend + minimal working frontend"
echo "This gives you a functional app immediately."
echo ""

echo "OPTION 2: Deploy backend only"  
echo "API-only deployment - you can test backend while fixing frontend."
echo ""

echo "OPTION 3: Try Node.js version downgrade"
echo "Use Node 18 which is known to work with React."
echo ""

read -p "Choose option (1/2/3): " option

case $option in
  1)
    echo ""
    echo "🎯 Creating minimal working frontend..."
    
    cd frontend
    
    # Create ultra-minimal package.json
    cat > package.json << 'EOF'
{
  "name": "grace-papers-gen-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^17.0.2",
    "react-dom": "^17.0.2",
    "react-scripts": "4.0.3"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
EOF
    
    # Create simple working App.js
    cat > src/App.js << 'EOF'
import React, { useState } from 'react';

function App() {
  const [query, setQuery] = useState('');
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);

  const searchCourses = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const response = await fetch('/api/search-courses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, k: 5 }),
      });
      const data = await response.json();
      setCourses(data.courses || []);
    } catch (error) {
      console.error('Search failed:', error);
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <h1>🎓 Grace Papers Gen</h1>
      <p>AI-Powered Learning Platform</p>
      
      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What would you like to learn?"
          style={{ width: '300px', padding: '10px', marginRight: '10px' }}
          onKeyPress={(e) => e.key === 'Enter' && searchCourses()}
        />
        <button onClick={searchCourses} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      <div>
        {courses.map((course) => (
          <div key={course.uuid} style={{ border: '1px solid #ccc', padding: '15px', margin: '10px 0' }}>
            <h3>{course.title}</h3>
            <p>{course.description}</p>
            <small>{course.provider} • {course.level}</small>
          </div>
        ))}
      </div>

      <p style={{ textAlign: 'center', color: '#666' }}>
        🚀 Backend Working • Frontend Simplified for Deployment
      </p>
    </div>
  );
}

export default App;
EOF
    
    # Create simple CSS
    cat > src/index.css << 'EOF'
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background-color: #f5f5f5;
}
EOF
    
    rm -rf node_modules package-lock.json
    npm install
    npm run build
    
    if [ $? -eq 0 ]; then
      echo "✅ Minimal frontend builds successfully!"
      cd ..
      git add .
      git commit -m "Deploy: Working minimal version - backend + simple frontend"
      git push origin main
      echo "🚀 Deployed! Check Vercel dashboard."
    else
      echo "❌ Even minimal version failed"
    fi
    ;;
    
  2)
    echo ""
    echo "🎯 Deploying backend only..."
    cp vercel-backend-only.json vercel.json
    git add .
    git commit -m "Deploy: Backend only - bypass frontend build issues"
    git push origin main
    echo "🚀 Backend-only deployment pushed!"
    ;;
    
  3)
    echo ""
    echo "🔄 Node.js version check..."
    echo "Current Node version: $(node --version)"
    echo ""
    echo "Recommended actions:"
    echo "1. Install Node Version Manager (nvm)"
    echo "2. nvm install 18"
    echo "3. nvm use 18"
    echo "4. Try building again"
    echo ""
    echo "After switching Node versions, run:"
    echo "./aggressive-fix.sh"
    ;;
    
  *)
    echo "Invalid option. Try again."
    ;;
esac
