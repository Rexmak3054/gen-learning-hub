# AI Learning Platform - Frontend

A React-based learning platform that helps corporate employees, especially women, discover and plan AI-powered upskilling courses.

## 🚀 Quick Start

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation & Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd /Users/hiufungmak/grace-papers-gen/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Open your browser:**
   The app will automatically open at `http://localhost:3000`

## 📁 Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── App.js
│   ├── AILearningPlatform.js
│   ├── index.js
│   └── index.css
├── package.json
├── tailwind.config.js
└── postcss.config.js
```

## 🔧 Integration with Research Agent

The frontend is designed to integrate with your existing research agent. Key integration points:

### API Endpoints Needed
Create these endpoints in your backend to connect with the research agent:

1. **Course Search:**
   ```
   POST /api/search-courses
   Body: { "query": "user search query", "k": 10 }
   Response: { "courses": [...] }
   ```

2. **Save Study Plan:**
   ```
   POST /api/save-study-plan
   Body: { "courses": [...], "userId": "user-id" }
   ```

3. **User Profile:**
   ```
   GET /api/user-profile
   Response: { "name": "...", "role": "...", ... }
   ```

### Connect to Your MCP Server
Replace the mock API calls in `searchCourses()` function with real calls to your research agent.

## 🎨 Features

- **AI-Powered Search** - Natural language course discovery
- **Smart Recommendations** - Vector similarity scoring
- **Learning Path Planning** - Priority-based course sequencing
- **Progress Tracking** - Personal dashboard and goals
- **Mobile Responsive** - Works on all devices

## 🛠 Available Scripts

- `npm start` - Runs the app in development mode
- `npm build` - Builds the app for production
- `npm test` - Launches the test runner
- `npm eject` - Ejects from Create React App (irreversible)

## 📱 Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## 🔗 Next Steps

1. Set up backend API routes
2. Connect to your MCP server
3. Add authentication
4. Implement real course data
5. Add manager dashboard