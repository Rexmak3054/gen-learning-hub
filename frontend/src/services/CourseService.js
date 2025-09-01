// API service for communicating with your research agent
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

class CourseService {
  static async searchCourses(query, k = 10) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/agent-search-courses`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, k }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error searching courses:', error);
      throw error;
    }
  }

  static async saveStudyPlan(courses, userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/save-study-plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ courses, userId }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error saving study plan:', error);
      throw error;
    }
  }

  static async getUserProfile(userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/user-profile/${userId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching user profile:', error);
      throw error;
    }
  }

  static async getStudyPlan(userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/study-plan/${userId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching study plan:', error);
      throw error;
    }
  }
}

export default CourseService;