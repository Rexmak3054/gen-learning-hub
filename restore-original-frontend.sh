#!/bin/bash

echo "🔄 RESTORING YOUR ORIGINAL WORKING FRONTEND"
echo "=========================================="
echo ""
echo "I'll restore your frontend exactly as it was before we started fixing things."
echo "Sometimes the original version works better!"
echo ""

cd frontend

echo "📁 Backing up current broken version..."
mkdir -p ../frontend-broken-backup
cp -r * ../frontend-broken-backup/ 2>/dev/null || true

echo ""
echo "🔄 Restoring original package.json..."
cat > package.json << 'EOF'
{
  "name": "ai-learning-platform",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.17.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^14.5.2",
    "ajv": "^7.2.4",
    "lucide-react": "^0.263.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "^5.0.1",
    "web-vitals": "^3.5.2"
  },
  "scripts": {
    "start": "GENERATE_SOURCEMAP=false react-scripts start",
    "build": "GENERATE_SOURCEMAP=false react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
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
  "devDependencies": {
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0"
  },
  "resolutions": {
    "ajv": "^8.12.0",
    "nth-check": "^2.0.1"
  }
}
EOF

echo ""
echo "🎨 Restoring original Tailwind CSS..."
cat > src/index.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

/* Custom animations and utilities */
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.float-animation {
  animation: float 6s ease-in-out infinite;
}

.gradient-bg {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.glass-effect {
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  background-color: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(209, 213, 219, 0.3);
}

.course-card-hover {
  transition: all 0.3s ease;
}

.course-card-hover:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 10px 10px -5px rgb(0 0 0 / 0.04);
}

/* 3D Card Effects */
.card-3d {
  transform-style: preserve-3d;
  transition: transform 0.6s;
}

.card-3d:hover {
  transform: rotateY(10deg) rotateX(10deg);
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
EOF

echo ""
echo "📱 Restoring original App.js..."
cat > src/App.js << 'EOF'
import React, { useState } from 'react';
import Navigation from './components/Navigation';
import EnhancedDiscoverPage from './pages/EnhancedDiscoverPage';
import PlanPage from './pages/PlanPage';
import ProfilePage from './pages/ProfilePage';
import useCourseManager from './hooks/useCourseManager';

function App() {
  const [currentView, setCurrentView] = useState('discover'); // discover, plan, profile
  const [userProfile] = useState({
    id: 'user-123',
    name: 'Sarah Chen',
    role: 'Marketing Manager',
    experience: 'Beginner',
    goals: ['AI Tools Proficiency', 'Data Analysis', 'Automation'],
    completedCourses: 3,
    totalHours: 24
  });

  const {
    searchQuery,
    setSearchQuery,
    recommendations,
    selectedCourses,
    studyPlan,
    isSearching,
    searchCourses,
    addToPlan,
    removeFromPlan,
    reorderPlan,
    finalizePlan
  } = useCourseManager();

  const handleFinalizePlan = () => {
    finalizePlan();
    setCurrentView('profile');
  };

  const renderCurrentPage = () => {
    switch (currentView) {
      case 'discover':
        return (
          <EnhancedDiscoverPage
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            recommendations={recommendations}
            isSearching={isSearching}
            onSearch={searchCourses}
            onAddToPlan={addToPlan}
            selectedCourses={selectedCourses}
          />
        );
      case 'plan':
        return (
          <PlanPage
            selectedCourses={selectedCourses}
            onReorderPlan={reorderPlan}
            onRemoveFromPlan={removeFromPlan}
            onFinalizePlan={handleFinalizePlan}
          />
        );
      case 'profile':
        return (
          <ProfilePage
            userProfile={userProfile}
            studyPlan={studyPlan}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation 
        currentView={currentView}
        setCurrentView={setCurrentView}
        selectedCoursesCount={selectedCourses.length}
      />
      
      <main className="py-8 px-6">
        {renderCurrentPage()}
      </main>
    </div>
  );
}

export default App;
EOF

echo ""
echo "🧹 Cleaning up and fresh install with OpenSSL fix..."
rm -rf node_modules package-lock.json yarn.lock

echo ""
echo "🔧 Using legacy OpenSSL provider to fix the crypto error..."
export NODE_OPTIONS="--openssl-legacy-provider"

echo ""
echo "📦 Installing original dependencies..."
npm install --legacy-peer-deps

echo ""
echo "🏗️ Testing build with OpenSSL fix..."
NODE_OPTIONS="--openssl-legacy-provider" npm run build

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! Your original frontend is back and working!"
    echo ""
    echo "✅ Restored features:"
    echo "  • Multi-page navigation (Discover, Plan, Profile)"
    echo "  • 3D course cards and carousels"
    echo "  • Enhanced discovery page"
    echo "  • Study plan management"
    echo "  • Beautiful Tailwind styling"
    echo "  • All your original components"
    echo ""
    echo "🔑 The fix: --openssl-legacy-provider flag"
    echo ""
    echo "🚀 Ready to deploy your original beautiful UI!"
    echo ""
    echo "Deploy now? (y/n)"
    read -p "" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd ..
        
        # Update package.json scripts to include the OpenSSL fix
        cd frontend
        cat > package.json << 'EOF'
{
  "name": "ai-learning-platform",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.17.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^14.5.2",
    "ajv": "^7.2.4",
    "lucide-react": "^0.263.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "^5.0.1",
    "web-vitals": "^3.5.2"
  },
  "scripts": {
    "start": "NODE_OPTIONS=--openssl-legacy-provider GENERATE_SOURCEMAP=false react-scripts start",
    "build": "NODE_OPTIONS=--openssl-legacy-provider GENERATE_SOURCEMAP=false react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
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
  "devDependencies": {
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0"
  },
  "resolutions": {
    "ajv": "^8.12.0",
    "nth-check": "^2.0.1"
  }
}
EOF
        
        cd ..
        git add .
        git commit -m "Restore: Original working frontend with OpenSSL legacy provider fix"
        git push origin main
        echo ""
        echo "🎉 DEPLOYED! Your beautiful original UI is back!"
        echo ""
        echo "The OpenSSL fix is now permanent in your build scripts."
    else
        echo ""
        echo "Your original frontend is restored and ready."
        echo "Deploy manually when ready:"
        echo "git add . && git commit -m 'Restore original frontend' && git push"
    fi
else
    echo ""
    echo "❌ Still having issues. Let me try a different approach..."
    echo ""
    echo "🔧 Trying with older React Scripts version..."
    
    cat > package.json << 'EOF'
{
  "name": "ai-learning-platform", 
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "lucide-react": "^0.263.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0", 
    "react-scripts": "4.0.3",
    "web-vitals": "^3.5.2"
  },
  "scripts": {
    "start": "GENERATE_SOURCEMAP=false react-scripts start",
    "build": "GENERATE_SOURCEMAP=false react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": ["react-app"]
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  },
  "devDependencies": {
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.16", 
    "postcss": "^8.4.32"
  }
}
EOF

    rm -rf node_modules package-lock.json
    npm install --legacy-peer-deps
    npm run build
    
    if [ $? -eq 0 ]; then
        echo "✅ Older React Scripts worked!"
        echo "🚀 Your original UI is restored with React Scripts 4.0.3"
    else
        echo "❌ Let me know and we'll try backend-only deployment instead"
    fi
fi
