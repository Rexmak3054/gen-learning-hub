// Enhanced Discover page with streaming chat and course cards
import React, { useState } from 'react';
import SearchBar from '../components/SearchBar';
import QuickStartCards from '../components/QuickStartCards';
import LoadingSpinner from '../components/LoadingSpinner';
import CourseCard from '../components/CourseCard';
import StreamingChatWithCourses from '../components/StreamingChatWithCourses';
import { MessageCircle, Search, BookOpen } from 'lucide-react';

const EnhancedDiscoverPage = ({ 
  searchQuery, 
  setSearchQuery, 
  recommendations, 
  isSearching, 
  onSearch, 
  onAddToPlan,
  selectedCourses 
}) => {
  const [activeMode, setActiveMode] = useState('chat'); // 'chat' or 'search'

  return (
    <div className="max-w-7xl mx-auto">
      {/* Mode Switcher */}
      <div className="mb-8">
        <div className="bg-white rounded-lg shadow-sm border p-1 inline-flex">
          <button
            onClick={() => setActiveMode('chat')}
            className={`px-4 py-2 rounded-md flex items-center gap-2 transition-all ${
              activeMode === 'chat'
                ? 'bg-purple-600 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <MessageCircle className="h-4 w-4" />
            Chat Mode
          </button>
          {/* <button
            onClick={() => setActiveMode('search')}
            className={`px-4 py-2 rounded-md flex items-center gap-2 transition-all ${
              activeMode === 'search'
                ? 'bg-purple-600 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <Search className="h-4 w-4" />
            Classic Search
          </button> */}
        </div>
      </div>

      {activeMode === 'chat' ? (
        /* Streaming Chat Mode */
        <div>
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              🤖 AI Learning Assistant
            </h1>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Have a natural conversation with our AI assistant. Ask about courses, get learning advice, 
              or chat about anything! The AI will automatically show course recommendations when relevant.
            </p>
          </div>
          
          <StreamingChatWithCourses 
            onAddToPlan={onAddToPlan}
            selectedCourses={selectedCourses}
          />
        </div>
      ) : (
        /* Classic Search Mode */
        <div>
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              🔍 Course Search
            </h1>
            <p className="text-gray-600">
              Search for courses using keywords and browse our recommendations.
            </p>
          </div>

          <SearchBar 
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            onSearch={onSearch}
            isSearching={isSearching}
          />

          <QuickStartCards onQuickSearch={onSearch} />

          {isSearching && (
            <LoadingSpinner message="Our AI is finding the best courses for you..." />
          )}

          {recommendations.length > 0 && !isSearching && (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                  <BookOpen className="h-6 w-6" />
                  AI Recommendations for "{searchQuery}"
                </h2>
                <span className="text-sm text-gray-500">
                  {recommendations.length} courses found
                </span>
              </div>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {recommendations.map((course) => (
                  <CourseCard 
                    key={course.uuid} 
                    course={course}
                    isInPlan={selectedCourses.some(c => c.uuid === course.uuid)}
                    showAddButton={true}
                    onAddToPlan={onAddToPlan}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Hint to try chat mode */}
          {!isSearching && recommendations.length === 0 && (
            <div className="text-center py-12">
              <MessageCircle className="h-16 w-16 mx-auto text-purple-300 mb-4" />
              <h3 className="text-xl font-semibold text-gray-700 mb-2">
                Want a more personalized experience?
              </h3>
              <p className="text-gray-600 mb-4">
                Try our new Chat Mode for a conversational course discovery experience!
              </p>
              <button
                onClick={() => setActiveMode('chat')}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                Switch to Chat Mode
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EnhancedDiscoverPage;