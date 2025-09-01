// CourseCard component with robust data type handling
import React from 'react';
import { BookOpen, Star, Users, Plus } from 'lucide-react';
import { formatEnrollmentCount, truncateText, getLevelColor, getPlatformColor } from '../utils/helpers';

// Helper function to safely get string value from various data types
const safeStringValue = (value, fallback = '') => {
  if (!value) return fallback;
  if (Array.isArray(value)) return value.join(', ');
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
};

// Helper function to safely get array from various data types
const safeArrayValue = (value) => {
  if (!value) return [];
  if (Array.isArray(value)) return value;
  if (typeof value === 'string') return value.split(',').map(s => s.trim());
  return [String(value)];
};

const CourseCard = ({ course, isInPlan = false, showAddButton = true, onAddToPlan }) => {
  // Robust field extraction
  const title = safeStringValue(course.title, 'Untitled Course');
  const provider = safeStringValue(course.provider || course.partner_primary || course.platform, 'Unknown Provider');
  const level = safeStringValue(course.level, 'All Levels').replace(/_/g, ' ');
  const description = safeStringValue(course.description || course.primary_description || course.summary, 'No description available');
  const platform = safeStringValue(course.platform, 'Unknown');
  const skills = safeArrayValue(course.skills);
  
  // Handle duration
  let duration = '';
  if (course.duration) {
    duration = safeStringValue(course.duration).replace(/_/g, ' ').toLowerCase();
  } else if (course.weeks_to_complete) {
    duration = `${course.weeks_to_complete} weeks`;
  }
  
  // Handle effort
  const effort = safeStringValue(course.effort || course.estimated_effort, '');
  
  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 border border-gray-100">
      <div className="relative">
        <img 
          src={course.img_url} 
          alt={title}
          className="w-full h-48 object-cover"
          onError={(e) => {
            e.target.src = `https://via.placeholder.com/300x200/6366f1/white?text=${encodeURIComponent(title.slice(0, 20))}`;
          }}
        />
        <div className={`absolute top-3 right-3 px-2 py-1 rounded-full text-xs font-medium ${getPlatformColor(platform)}`}>
          {platform}
        </div>
        {course.similarity_score && (
          <div className="absolute top-3 left-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-2 py-1 rounded-full text-xs font-medium">
            {Math.round(course.similarity_score * 100)}% match
          </div>
        )}
      </div>
      
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-bold text-gray-900 line-clamp-2">{title}</h3>
          {showAddButton && !isInPlan && (
            <button
              onClick={() => onAddToPlan(course)}
              className="ml-2 p-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition-colors flex-shrink-0"
              title="Add to learning plan"
            >
              <Plus className="h-4 w-4" />
            </button>
          )}
        </div>
        
        <p className="text-gray-600 text-sm mb-4 line-clamp-3">
          {truncateText(description, 120)}
        </p>
        
        <div className="space-y-2 mb-4">
          <div className="flex items-center text-sm text-gray-500">
            <Users className="h-4 w-4 mr-2" />
            <span>{provider}</span>
          </div>
          <div className="flex items-center text-sm text-gray-500">
            <BookOpen className="h-4 w-4 mr-2" />
            <span className={`px-2 py-1 rounded text-xs ${getLevelColor(level)}`}>
              {level}
            </span>
            {duration && <span className="ml-2">{duration}</span>}
            {effort && <span className="ml-2">• {effort}</span>}
          </div>
          {course.enrol_cnt && (
            <div className="flex items-center text-sm text-gray-500">
              <Star className="h-4 w-4 mr-2" />
              <span>{formatEnrollmentCount(course.enrol_cnt)} students enrolled</span>
            </div>
          )}
        </div>
        
        {skills.length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-1">
              {skills.slice(0, 5).map((skill, idx) => (
                <span key={idx} className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                  {String(skill).trim()}
                </span>
              ))}
            </div>
          </div>
        )}
        
        <button 
          className="w-full bg-gray-900 text-white py-2 px-4 rounded-lg hover:bg-gray-800 transition-colors text-sm font-medium"
          onClick={() => window.open(course.url, '_blank')}
        >
          View Course Details
        </button>
      </div>
    </div>
  );
};

export default CourseCard;