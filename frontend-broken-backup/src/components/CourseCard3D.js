import React from 'react';
import { Users, BookOpen, Star, Plus } from 'lucide-react';

const formatEnrollmentCount = (count) => {
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
  if (count >= 1000) return `${(count / 1000).toFixed(0)}k`;
  return count.toString();
};

const truncateText = (text, maxLength) => {
  if (!text || text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

const stripTags = (s = '') => s.replace(/<[^>]*>/g, '').trim();

const getLevelColor = (level) => {
  const levelLower = level.toLowerCase();
  if (levelLower.includes('beginner')) return 'bg-green-100 text-green-700';
  if (levelLower.includes('intermediate')) return 'bg-yellow-100 text-yellow-700';
  if (levelLower.includes('advanced')) return 'bg-red-100 text-red-700';
  return 'bg-gray-100 text-gray-700';
};

const getPlatformColor = (platform) => {
  const platformLower = platform.toLowerCase();
  if (platformLower.includes('udemy')) return 'bg-purple-100 text-purple-700';
  if (platformLower.includes('edx')) return 'bg-blue-100 text-blue-700';
  if (platformLower.includes('coursera')) return 'bg-blue-100 text-blue-700';
  return 'bg-gray-100 text-gray-700';
};

const safeStringValue = (value, fallback = '') => {
  if (!value) return fallback;
  if (Array.isArray(value)) return value.join(', ');
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
};

const safeArrayValue = (value) => {
  if (!value) return [];
  if (Array.isArray(value)) return value;
  if (typeof value === 'string') return value.split(',').map(s => s.trim());
  return [String(value)];
};

const toSkillText = (s) =>
  typeof s === 'string'
    ? s
    : s?.name || s?.title || s?.skill || s?.label || '';

const CourseCard3D = ({ course, isActive, isInPlan, onAddToPlan }) => {
  const title = safeStringValue(course.title, 'Untitled Course');
  const provider = safeStringValue(course.provider || course.partner_primary || course.platform, 'Unknown Provider');
  const level = safeStringValue(course.level, 'All Levels').replace(/_/g, ' ');
  const descriptionRaw = safeStringValue(course.description || course.primary_description || course.summary, 'No description available');
  const description = stripTags(descriptionRaw);
  const platform = safeStringValue(course.platform, 'Unknown');
  const skills = safeArrayValue(course.skills).map(toSkillText).filter(Boolean);

  let duration = '';
  if (course.duration) {
    duration = String(course.duration).replace(/_/g, ' ').toLowerCase();
  } else if (course.weeks_to_complete) {
    duration = `${course.weeks_to_complete} weeks`;
  }

  const effort = course.effort || course.estimated_effort || '';

  return (
    <div className={`w-full max-w-sm bg-white rounded-2xl shadow-2xl transition-all duration-300 ${isActive ? 'shadow-purple-500/20' : ''}`}>
      {/* Image */}
      <div className="relative h-48 overflow-hidden">
        <img
          src={course.img_url}
          alt={title}
          className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
          onError={(e) => {
            e.target.src = `https://via.placeholder.com/300x200/6366f1/white?text=${encodeURIComponent(title.slice(0, 20))}`;
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />

        {/* Platform badge */}
        <div className={`absolute top-3 right-3 px-3 py-1 rounded-full text-xs font-medium backdrop-blur-sm ${getPlatformColor(platform)}`}>
          {platform}
        </div>

        {/* Add button */}
        {isActive && !isInPlan && onAddToPlan && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onAddToPlan(course);
            }}
            className="absolute bottom-3 right-3 p-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full hover:from-purple-600 hover:to-pink-600 transition-all transform hover:scale-110 shadow-lg"
            title="Add to learning plan"
          >
            <Plus className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Content */}
      <div className="p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-3 leading-tight">
          {title}
        </h3>

        <p className="text-gray-600 text-sm mb-4 leading-relaxed">
          {truncateText(description, 120)}
        </p>

        {/* Course details */}
        <div className="space-y-3 mb-4">
          <div className="flex items-center text-sm text-gray-500">
            <Users className="h-4 w-4 mr-2 text-purple-500" />
            <span className="font-medium">{provider}</span>
          </div>

          <div className="flex items-center text-sm text-gray-500">
            <BookOpen className="h-4 w-4 mr-2 text-blue-500" />
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getLevelColor(level)}`}>
              {level}
            </span>
            {duration && <span className="ml-2 text-gray-600">{duration}</span>}
            {effort && <span className="ml-2 text-gray-400">• {effort}</span>}
          </div>

          {course.enrol_cnt && (
            <div className="flex items-center text-sm text-gray-500">
              <Star className="h-4 w-4 mr-2 text-yellow-500" />
              <span>{formatEnrollmentCount(course.enrol_cnt)} students</span>
            </div>
          )}
        </div>

        {/* Skills */}
        {skills.length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-1">
              {skills.slice(0, 4).map((skill, idx) => (
                <span key={idx} className="px-2 py-1 bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 text-xs rounded-full font-medium">
                  {skill}
                </span>
              ))}
              {skills.length > 4 && (
                <span className="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded-full">
                  +{skills.length - 4} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Button */}
        <button
          className="w-full bg-gradient-to-r from-gray-800 to-gray-900 text-white py-3 px-4 rounded-xl hover:from-gray-700 hover:to-gray-800 transition-all text-sm font-medium transform hover:scale-105 shadow-lg"
          onClick={(e) => {
            e.stopPropagation();
            window.open(course.url, '_blank');
          }}
        >
          View Course Details
        </button>
      </div>
    </div>
  );
};

export default CourseCard3D;