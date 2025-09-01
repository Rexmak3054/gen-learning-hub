# AI Learning Platform - Frontend Structure

## 📁 Project Structure

```
frontend/
├── public/
│   ├── index.html              # Main HTML template
│   └── manifest.json           # PWA manifest
├── src/
│   ├── components/             # Reusable UI components
│   │   ├── CourseCard.js       # Individual course display card
│   │   ├── LoadingSpinner.js   # Loading animation component
│   │   ├── Navigation.js       # Top navigation bar
│   │   ├── PlanItem.js         # Study plan list item
│   │   ├── QuickStartCards.js  # Quick start suggestion cards
│   │   ├── SearchBar.js        # AI-powered search interface
│   │   └── index.js            # Component exports
│   ├── pages/                  # Main page components
│   │   ├── DiscoverPage.js     # Course discovery page
│   │   ├── PlanPage.js         # Learning plan management
│   │   ├── ProfilePage.js      # User profile and progress
│   │   └── index.js            # Page exports
│   ├── hooks/                  # Custom React hooks
│   │   └── useCourseManager.js # Course state management
│   ├── services/               # API communication
│   │   └── CourseService.js    # Research agent integration
│   ├── utils/                  # Helper functions and constants
│   │   ├── constants.js        # Mock data and constants
│   │   └── helpers.js          # Utility functions
│   ├── App.js                  # Main app component
│   ├── index.js                # React app entry point
│   └── index.css               # Global styles and Tailwind
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── package.json                # Dependencies and scripts
├── postcss.config.js           # PostCSS configuration
├── tailwind.config.js          # Tailwind CSS configuration
└── README.md                   # Setup instructions
```

## 🔧 Component Architecture

### **Pages** (Main Views)
- **DiscoverPage** - AI-powered course search and recommendations
- **PlanPage** - Learning plan builder with priority ordering
- **ProfilePage** - User dashboard with progress and goals

### **Components** (Reusable UI)
- **CourseCard** - Displays course info with similarity scores
- **SearchBar** - Natural language search interface
- **Navigation** - Top navigation with active states
- **QuickStartCards** - Predefined learning paths
- **LoadingSpinner** - Loading states with animations
- **PlanItem** - Individual course in learning plan

### **Hooks** (State Management)
- **useCourseManager** - Manages all course-related state and operations

### **Services** (API Layer)
- **CourseService** - Communicates with your research agent backend

### **Utils** (Helper Functions)
- **constants.js** - Mock data, quick start options, user roles
- **helpers.js** - Formatting, calculations, utility functions

## 🚀 Getting Started

```bash
cd /Users/hiufungmak/grace-papers-gen/frontend
npm install
npm start
```

## 🔗 Integration Points

The frontend is structured to easily integrate with your research agent:

1. **Update CourseService.js** with your API endpoints
2. **Modify useCourseManager.js** to use real API calls
3. **Set REACT_APP_ENABLE_MOCK_DATA=false** in .env to use real data

## 📱 Features

- **Responsive Design** - Mobile-first approach
- **Modern UI** - Purple/pink gradient theme
- **Accessibility** - Proper ARIA labels and keyboard navigation
- **Performance** - Optimized components and lazy loading ready
- **Extensible** - Easy to add new features and components