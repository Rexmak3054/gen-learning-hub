// Navigation component
import React from 'react';
import { Sparkles } from 'lucide-react';

const Navigation = ({ currentView, setCurrentView, selectedCoursesCount }) => {
  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Sparkles className="h-8 w-8 text-purple-500 mr-3" />
            <span className="text-xl font-bold text-gray-900">GEN Learning Hub</span>
          </div>
          
          <div className="flex space-x-8">
            <button
              onClick={() => setCurrentView('discover')}
              className={`px-3 py-2 text-sm font-medium transition-colors ${
                currentView === 'discover' 
                  ? 'text-purple-600 border-b-2 border-purple-600' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Discover
            </button>
            <button
              onClick={() => setCurrentView('plan')}
              className={`px-3 py-2 text-sm font-medium transition-colors relative ${
                currentView === 'plan' 
                  ? 'text-purple-600 border-b-2 border-purple-600' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              My Plan
              {selectedCoursesCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {selectedCoursesCount}
                </span>
              )}
            </button>
            <button
              onClick={() => setCurrentView('profile')}
              className={`px-3 py-2 text-sm font-medium transition-colors ${
                currentView === 'profile' 
                  ? 'text-purple-600 border-b-2 border-purple-600' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Profile
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;