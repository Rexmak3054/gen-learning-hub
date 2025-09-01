// Discover page
import React from 'react';
import SearchBar from '../components/SearchBar';
import QuickStartCards from '../components/QuickStartCards';
import LoadingSpinner from '../components/LoadingSpinner';
import CourseCard from '../components/CourseCard';

const DiscoverPage = ({ 
  searchQuery, 
  setSearchQuery, 
  recommendations, 
  isSearching, 
  onSearch, 
  onAddToPlan,
  selectedCourses 
}) => {
  return (
    <div className="max-w-7xl mx-auto">
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
            <h2 className="text-2xl font-bold text-gray-900">
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
    </div>
  );
};

export default DiscoverPage;