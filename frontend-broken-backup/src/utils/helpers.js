// Utility functions
export const formatDuration = (duration, effort) => {
  const weeks = parseInt(duration?.split(' ')[0]) || 0;
  const hoursPerWeek = parseInt(effort?.split('-')[0]) || 0;
  return weeks * hoursPerWeek;
};

export const formatEnrollmentCount = (count) => {
  if (!count) return '0';
  return count.toLocaleString();
};

export const truncateText = (text, maxLength = 150) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export const getLevelColor = (level) => {
  switch (level?.toLowerCase()) {
    case 'beginner':
      return 'bg-green-100 text-green-700';
    case 'intermediate':
      return 'bg-yellow-100 text-yellow-700';
    case 'advanced':
      return 'bg-red-100 text-red-700';
    default:
      return 'bg-gray-100 text-gray-700';
  }
};

export const getPlatformColor = (platform) => {
  switch (platform?.toLowerCase()) {
    case 'coursera':
      return 'bg-blue-100 text-blue-700';
    case 'edx':
      return 'bg-purple-100 text-purple-700';
    case 'udemy':
      return 'bg-orange-100 text-orange-700';
    default:
      return 'bg-gray-100 text-gray-700';
  }
};

export const calculateTotalStudyTime = (courses) => {
  return courses.reduce((acc, course) => {
    return acc + formatDuration(course.duration, course.effort);
  }, 0);
};

export const generateUserInitials = (name) => {
  if (!name) return 'U';
  return name.split(' ').map(n => n[0]).join('').toUpperCase();
};