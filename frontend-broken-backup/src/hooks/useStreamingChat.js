import { useState, useCallback, useRef } from 'react';
import { ChatService } from '../services/ChatService';

/**
 * Custom hook for managing streaming chat with course recommendations
 */
export const useStreamingChat = () => {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [courses, setCourses] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [currentQuery, setCurrentQuery] = useState('');
  const [error, setError] = useState(null);

  // Initialize chat session
  const initializeChat = useCallback(async (userId = null) => {
    try {
      setError(null);
      const result = await ChatService.startChatSession(userId);
      console.log(result)
      if (result) {
        setSessionId(result.session_id);
        setIsConnected(true);
        setMessages([]);
        setCourses([]);
        return result.session_id;
      } else {
        throw new Error(result.error || 'Failed to start chat session');
      }
    } catch (error) {
      console.error('Failed to initialize chat:', error);
      setError(error.message);
      setIsConnected(false);
      return null;
    }
  }, []);

  // Send a message and handle streaming response
  const sendMessage = useCallback(async (message) => {
    if (!sessionId || !message.trim()) return;

    try {
      setError(null);
      setIsStreaming(true);

      // Add user message to local state
      const userMessage = {
        id: Date.now().toString(),
        message_type: 'user',
        content: message,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, userMessage]);

      // Start streaming
      await ChatService.streamChatMessage(sessionId, message, {
        onMessage: (messageData) => {
          const agentMessage = {
            id: messageData.id,
            message_type: messageData.message_type,
            content: messageData.content,
            timestamp: messageData.timestamp
          };
          
          setMessages(prev => [...prev, agentMessage]);
        },
        
        onCoursesReady: ({ courses, totalResults, query, isUpdate }) => {
          console.log(`📚 Courses ready: ${courses.length} courses${isUpdate ? ' (updated)' : ''}`);
          console.log('Courses data:', courses);
          setCourses(courses);
          setCurrentQuery(query);
          
          // If this is an update, we could add a visual indicator
          if (isUpdate) {
            // You could trigger a visual update animation here
            console.log('🔄 Course recommendations updated');
          }
        },
        
        onComplete: (data) => {
          console.log('✅ Streaming completed:', data);
          setIsStreaming(false);
        },
        
        onError: (errorMessage) => {
          console.error('❌ Streaming error:', errorMessage);
          setError(errorMessage);
          setIsStreaming(false);
        }
      });

    } catch (error) {
      console.error('Error sending message:', error);
      setError(error.message);
      setIsStreaming(false);
    }
  }, [sessionId]);

  // Clear current courses (useful when starting a new search topic)
  const clearCourses = useCallback(() => {
    setCourses([]);
    setCurrentQuery('');
  }, []);

  // Reset the entire chat
  const resetChat = useCallback(async (userId = null) => {
    setMessages([]);
    setCourses([]);
    setCurrentQuery('');
    setError(null);
    setIsStreaming(false);
    
    const newSessionId = await initializeChat(userId);
    return newSessionId;
  }, [initializeChat]);

  return {
    // State
    sessionId,
    messages,
    courses,
    isStreaming,
    isConnected,
    currentQuery,
    error,
    
    // Actions
    initializeChat,
    sendMessage,
    clearCourses,
    resetChat
  };
};