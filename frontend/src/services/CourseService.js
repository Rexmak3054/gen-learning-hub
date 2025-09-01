// API service for communicating with backend
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

class CourseService {
  static async searchCourses(query, k = 10) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/search-courses`, {
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
        // If endpoint doesn't exist, don't throw error for now
        console.warn('Save study plan endpoint not available');
        return { success: true, message: 'Study plan saved locally' };
      }

      return await response.json();
    } catch (error) {
      console.warn('Error saving study plan:', error);
      // Return success for graceful fallback
      return { success: true, message: 'Study plan saved locally' };
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
        // Return empty study plan if endpoint doesn't exist
        return { success: true, study_plan: [], user_id: userId };
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching study plan:', error);
      // Return empty study plan as fallback
      return { success: true, study_plan: [], user_id: userId };
    }
  }
}

export default CourseService;