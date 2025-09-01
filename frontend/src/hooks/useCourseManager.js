// Custom hook for course management
import { useState } from 'react';
import CourseService from '../services/CourseService';
import { MOCK_COURSES } from '../utils/constants';

const useCourseManager = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [selectedCourses, setSelectedCourses] = useState([]);
  const [studyPlan, setStudyPlan] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  const searchCourses = async (query) => {
    setIsSearching(true);
    setSearchQuery(query);
    
    try {
      // Check if we should use mock data
      const useMockData = process.env.REACT_APP_ENABLE_MOCK_DATA === 'true';
      
      if (useMockData) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        setRecommendations(MOCK_COURSES);
      } else {
        // Use real API
        const data = await CourseService.searchCourses(query, 10);
        setRecommendations(data.courses || []);
      }
    } catch (error) {
      console.error('Error searching courses:', error);
      setRecommendations([]);
    } finally {
      setIsSearching(false);
    }
  };

  const addToPlan = (course) => {
    if (!selectedCourses.find(c => c.uuid === course.uuid)) {
      setSelectedCourses([...selectedCourses, { ...course, priority: selectedCourses.length + 1 }]);
    }
  };

  const removeFromPlan = (courseId) => {
    const newCourses = selectedCourses.filter(c => c.uuid !== courseId);
    // Re-prioritize remaining courses
    newCourses.forEach((course, index) => {
      course.priority = index + 1;
    });
    setSelectedCourses(newCourses);
  };

  const reorderPlan = (courseId, direction) => {
    const currentIndex = selectedCourses.findIndex(c => c.uuid === courseId);
    if (currentIndex === -1) return;
    
    const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
    if (newIndex < 0 || newIndex >= selectedCourses.length) return;
    
    const newCourses = [...selectedCourses];
    [newCourses[currentIndex], newCourses[newIndex]] = [newCourses[newIndex], newCourses[currentIndex]];
    
    // Update priorities
    newCourses.forEach((course, index) => {
      course.priority = index + 1;
    });
    
    setSelectedCourses(newCourses);
  };

  const finalizePlan = async (userId = 'user-123') => {
    try {
      const useMockData = process.env.REACT_APP_ENABLE_MOCK_DATA === 'true';
      
      if (!useMockData) {
        await CourseService.saveStudyPlan(selectedCourses, userId);
      }
      
      setStudyPlan([...selectedCourses]);
      setSelectedCourses([]);
    } catch (error) {
      console.error('Error saving study plan:', error);
      // Still update local state even if API fails
      setStudyPlan([...selectedCourses]);
      setSelectedCourses([]);
    }
  };

  return {
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
  };
};

export default useCourseManager;