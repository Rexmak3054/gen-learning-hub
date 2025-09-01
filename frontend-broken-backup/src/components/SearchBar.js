// SearchBar component
import React from 'react';
import { Search, Sparkles } from 'lucide-react';

const SearchBar = ({ searchQuery, setSearchQuery, onSearch, isSearching }) => {
  return (
    <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl p-8 mb-8 text-white">
      <div className="max-w-4xl mx-auto text-center">
        <div className="flex items-center justify-center mb-4">
          <Sparkles className="h-8 w-8 mr-3" />
          <h1 className="text-3xl font-bold">AI-Powered Course Discovery</h1>
        </div>
        <p className="text-purple-100 mb-6 text-lg">
          Tell us what you want to learn, and our AI will find the perfect courses for your career growth
        </p>
        
        <div className="relative max-w-2xl mx-auto">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="e.g., 'I want to learn AI tools for content creation and social media management'"
            className="w-full pl-12 pr-4 py-4 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-4 focus:ring-purple-300 text-lg"
            onKeyPress={(e) => e.key === 'Enter' && onSearch(searchQuery)}
          />
          <button
            onClick={() => onSearch(searchQuery)}
            disabled={isSearching || !searchQuery}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-gray-900 text-white px-6 py-2 rounded-lg hover:bg-gray-800 disabled:opacity-50 transition-colors font-medium"
          >
            {isSearching ? 'Searching...' : 'Find Courses'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SearchBar;