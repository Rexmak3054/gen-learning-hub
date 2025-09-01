import React, { useEffect, useState, useRef } from 'react';
import { useStreamingChat } from '../hooks/useStreamingChat';
import CourseCard from './CourseCard';
import { Send, MessageCircle, RefreshCw, User, Bot, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';

const StreamingChatWithCourses = ({ onAddToPlan, selectedCourses = [] }) => {
  const {
    sessionId,
    messages,
    courses,
    isStreaming,
    isConnected,
    currentQuery,
    error,
    initializeChat,
    sendMessage,
    resetChat
  } = useStreamingChat();

  const [inputMessage, setInputMessage] = useState('');
  const [showCourses, setShowCourses] = useState(false);
  const [copiedMessageId, setCopiedMessageId] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize chat on component mount
  useEffect(() => {
    initializeChat();
  }, [initializeChat]);

  // Show courses section when courses are available
  useEffect(() => {
    setShowCourses(courses.length > 0);
  }, [courses]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isStreaming) return;
    
    await sendMessage(inputMessage);
    setInputMessage('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const copyToClipboard = async (text, messageId) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // Enhanced message component
  const ChatMessage = ({ message, isLast }) => {
    const isUser = message.message_type === 'user';
    const isStreaming = isLast && message.message_type === 'assistant' && message.isStreaming;

    return (
      <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} group`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser 
            ? 'bg-purple-600 text-white' 
            : 'bg-gray-200 text-gray-600'
        }`}>
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </div>

        {/* Message Content */}
        <div className={`flex flex-col max-w-[70%] ${isUser ? 'items-end' : 'items-start'}`}>
          {/* Message Bubble */}
          <div
            className={`px-4 py-3 rounded-2xl relative ${
              isUser
                ? 'bg-purple-600 text-white rounded-br-md'
                : 'bg-gray-100 text-gray-800 rounded-bl-md'
            } ${isStreaming ? 'animate-pulse' : ''}`}
          >
            {/* Message Text with better formatting */}
            <div className="whitespace-pre-wrap break-words leading-relaxed">
              {message.content}
            </div>

            {/* Streaming indicator */}
            {isStreaming && (
              <div className="flex items-center gap-1 mt-2 text-xs opacity-70">
                <RefreshCw className="h-3 w-3 animate-spin" />
                <span>AI is typing...</span>
              </div>
            )}
          </div>

          {/* Message Actions & Timestamp */}
          <div className={`flex items-center gap-2 mt-1 px-2 ${
            isUser ? 'flex-row-reverse' : 'flex-row'
          }`}>
            {/* Timestamp */}
            <span className="text-xs text-gray-400">
              {message.timestamp ? formatTimestamp(message.timestamp) : 'Just now'}
            </span>

            {/* Action buttons (only for assistant messages) */}
            {!isUser && (
              <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => copyToClipboard(message.content, message.id)}
                  className="p-1 hover:bg-gray-200 rounded text-gray-500 hover:text-gray-700"
                  title="Copy message"
                >
                  <Copy className="h-3 w-3" />
                </button>
                <button
                  className="p-1 hover:bg-gray-200 rounded text-gray-500 hover:text-green-600"
                  title="Good response"
                >
                  <ThumbsUp className="h-3 w-3" />
                </button>
                <button
                  className="p-1 hover:bg-gray-200 rounded text-gray-500 hover:text-red-600"
                  title="Poor response"
                >
                  <ThumbsDown className="h-3 w-3" />
                </button>
              </div>
            )}

            {/* Copy confirmation */}
            {copiedMessageId === message.id && (
              <span className="text-xs text-green-600 animate-fade-in">
                Copied!
              </span>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Enhanced Chat Section */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden flex flex-col">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold flex items-center gap-2">
                  <MessageCircle className="h-5 w-5" />
                  AI Course Assistant
                </h2>
                <p className="text-purple-100 mt-1">
                  {isConnected ? 'Connected - Ask me about courses!' : 'Connecting...'}
                </p>
              </div>
              <button
                onClick={resetChat}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                title="Reset chat"
              >
                <RefreshCw className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Status Bar */}
          {error && (
            <div className="bg-red-50 text-red-600 p-3 border-l-4 border-red-400">
              ⚠️ {error}
            </div>
          )}

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6 min-h-96 max-h-96">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
                <div className="bg-gray-100 rounded-full p-4 mb-4">
                  <MessageCircle className="h-8 w-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-700 mb-2">
                  Welcome! How can I help you today?
                </h3>
                <p className="text-sm text-gray-500 mb-4">
                  I can answer questions, recommend courses, or just chat!
                </p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {["Hello!", "I want to learn Python", "What's trending in tech?"].map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => setInputMessage(suggestion)}
                      className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-xs text-gray-600 transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((message, index) => (
                  <ChatMessage 
                    key={message.id} 
                    message={message} 
                    isLast={index === messages.length - 1}
                  />
                ))}
                
                {/* Streaming indicator */}
                {isStreaming && (
                  <div className="flex gap-3">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center">
                      <Bot className="h-4 w-4" />
                    </div>
                    <div className="bg-gray-100 text-gray-800 px-4 py-3 rounded-2xl rounded-bl-md">
                      <div className="flex items-center gap-2">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                        </div>
                        <span className="text-sm text-gray-500">AI is thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Enhanced Input Section */}
          <div className="p-6 border-t bg-gray-50">
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything or request courses..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none transition-all"
                  disabled={!isConnected || isStreaming}
                  rows={inputMessage.split('\n').length}
                  style={{ minHeight: '44px', maxHeight: '120px' }}
                />
                {inputMessage && (
                  <div className="absolute bottom-2 right-2 text-xs text-gray-400">
                    {inputMessage.length}/1000
                  </div>
                )}
              </div>
              <button
                onClick={handleSendMessage}
                disabled={!isConnected || isStreaming || !inputMessage.trim()}
                className="px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all hover:shadow-lg"
              >
                <Send className="h-4 w-4" />
                <span className="hidden sm:inline">Send</span>
              </button>
            </div>
            
            {/* Connection status */}
            <div className="flex items-center justify-between mt-2">
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                {isConnected ? 'Connected' : 'Disconnected'}
              </div>
              <div className="text-xs text-gray-400">
                Press Enter to send, Shift+Enter for new line
              </div>
            </div>
          </div>
        </div>

        {/* Course Cards Section - keeping your existing structure */}
        <div className="bg-white rounded-xl shadow-lg">
          <div className="p-6 border-b">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              📚 Course Recommendations
            </h2>
            
          </div>

          <div className="p-6">
            {courses.length === 0 ? (
              <div className="text-center text-gray-500 py-12">
                <div className="text-4xl mb-4">💡</div>
                <p>Ask about courses to see recommendations here</p>
                <p className="text-sm mt-2 text-gray-400">
                  The AI will find the best courses for your learning goals
                </p>
              </div>
            ) : (
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {courses.map((course) => (
                  <CourseCard
                    key={course.uuid}
                    course={course}
                    isInPlan={selectedCourses.some(c => c.uuid === course.uuid)}
                    showAddButton={!!onAddToPlan}
                    onAddToPlan={onAddToPlan}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Keep your existing quick actions */}
      {showCourses ? (
        <div className="mt-6 text-center">
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-blue-800 mb-3">
              💡 Try refining: "Actually, I want more advanced courses" or "Show me free options instead"
            </p>
            <div className="flex gap-2 justify-center flex-wrap">
              <button
                onClick={() => sendMessage("Show me more advanced options")}
                className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200"
                disabled={isStreaming}
              >
                More Advanced
              </button>
              <button
                onClick={() => sendMessage("I need beginner-friendly courses")}
                className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm hover:bg-green-200"
                disabled={isStreaming}
              >
                Beginner Level
              </button>
              <button
                onClick={() => sendMessage("Find me free courses")}
                className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm hover:bg-purple-200"
                disabled={isStreaming}
              >
                Free Courses
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="mt-6 text-center">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-gray-600 mb-3">
              💬 I can help with any question! Try asking about:
            </p>
            <div className="flex gap-2 justify-center flex-wrap">
              <button
                onClick={() => sendMessage("What's the latest in AI technology?")}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200"
                disabled={isStreaming}
              >
                AI Technology
              </button>
              <button
                onClick={() => sendMessage("I want to learn programming")}
                className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm hover:bg-purple-200"
                disabled={isStreaming}
              >
                Programming
              </button>
              <button
                onClick={() => sendMessage("How can I improve my career?")}
                className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm hover:bg-green-200"
                disabled={isStreaming}
              >
                Career Advice
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add some custom animations */}
      <style jsx>{`
        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        .animate-fade-in {
          animation: fade-in 0.3s ease-in-out;
        }
      `}</style>
    </div>
  );
};

export default StreamingChatWithCourses;