// Enhanced CourseService with streaming chat support
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ChatService {
  /**
   * Start a new chat session
   */
  static async startChatSession(userId = null) {
    try {
      console.log('🔌 Attempting to connect to:', `${API_BASE_URL}/api/chat/start`);
      
      const response = await fetch(`${API_BASE_URL}/api/chat/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId }),
      });

      console.log('📡 Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Backend response error:', errorText);
        throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('✅ Chat session started:', result);
      return result;
    } catch (error) {
      console.error('Error starting chat session:', error);
      console.error('API_BASE_URL:', API_BASE_URL);
      throw error;
    }
  }

  /**
   * Stream a chat message and handle real-time responses
   * @param {string} sessionId - The chat session ID
   * @param {string} message - User's message
   * @param {Object} callbacks - Event handlers for different stream events
   * @param {Function} callbacks.onMessage - Called when agent sends a message
   * @param {Function} callbacks.onCoursesReady - Called when courses are ready to display
   * @param {Function} callbacks.onComplete - Called when streaming is complete
   * @param {Function} callbacks.onError - Called when an error occurs
   */
  static async streamChatMessage(sessionId, message, callbacks = {}) {
    try {
      console.log('🚀 Starting stream chat to:', `${API_BASE_URL}/api/chat/stream`);
      console.log('📝 Message:', message);
      console.log('🆔 Session ID:', sessionId);
      
      const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: message
        })
      });

      console.log('📡 Stream response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Stream response error:', errorText);
        throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ') && line.length > 6) {
            try {
              const jsonStr = line.slice(6).trim();
              
              // Skip empty data lines
              if (!jsonStr) continue;
              
              console.log('📜 Parsing SSE line:', jsonStr.substring(0, 100) + (jsonStr.length > 100 ? '...' : ''));
              const data = JSON.parse(jsonStr);
              console.log('✅ Parsed SSE data:', data.event, data.data);
              
              switch (data.event) {
                case 'message_added':
                  if (data.data.message_type !== 'user' && callbacks.onMessage) {
                    // Additional check to avoid echoes and JSON responses
                    const content = data.data.content;
                    if (content && !ChatService.isUserMessageEcho(content, message) && !ChatService.isJsonContent(content)) {
                      callbacks.onMessage(data.data);
                    }
                  }
                  break;
                  
                case 'courses_ready':
                  if (callbacks.onCoursesReady) {
                    callbacks.onCoursesReady({
                      courses: data.data.courses,
                      totalResults: data.data.total_results,
                      query: data.data.query,
                      isUpdate: data.data.is_update || false
                    });
                  }
                  break;
                  
                case 'stream_complete':
                  if (callbacks.onComplete) {
                    callbacks.onComplete(data.data);
                  }
                  break;
                  
                case 'stream_error':
                  if (callbacks.onError) {
                    callbacks.onError(data.data.error);
                  }
                  break;
              }
            } catch (e) {
              console.warn('Failed to parse SSE line:', line.substring(0, 100) + '...');
              console.warn('Parse error:', e.message);
              // Continue processing other lines
            }
          }
        }
      }
    } catch (error) {
      console.error('Error in stream chat:', error);
      if (callbacks.onError) {
        callbacks.onError(error.message);
      }
      throw error;
    }
  }

  /**
   * Check if agent response is echoing the user's message
   */
  static isUserMessageEcho(content, userMessage) {
    if (!content || !userMessage) return false;
    
    const contentLower = content.toLowerCase().trim();
    const userLower = userMessage.toLowerCase().trim();
    
    // Exact match
    if (contentLower === userLower) return true;
    
    // High similarity (user message makes up >80% of content)
    if (userLower.length > 10 && contentLower.includes(userLower)) {
      const similarity = userLower.length / contentLower.length;
      if (similarity > 0.8) return true;
    }
    
    return false;
  }
  
  /**
   * Check if content is JSON data
   */
  static isJsonContent(content) {
    if (!content || typeof content !== 'string') return false;
    
    const trimmed = content.trim();
    if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || 
        (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
      try {
        const parsed = JSON.parse(trimmed);
        // If it has course-like structure, it's probably tool output
        if (typeof parsed === 'object' && ('courses' in parsed || 'success' in parsed)) {
          return true;
        }
      } catch (e) {
        // Not valid JSON
      }
    }
    
    return false;
  }

  /**
   * Get chat history for a session
   */
  static async getChatHistory(sessionId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/history/${sessionId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting chat history:', error);
      throw error;
    }
  }
}

// Enhanced CourseService with existing functionality
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

  static async getCourseDetails(courseId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/course/${courseId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching course details:', error);
      throw error;
    }
  }
}

export { ChatService, CourseService };
export default CourseService;