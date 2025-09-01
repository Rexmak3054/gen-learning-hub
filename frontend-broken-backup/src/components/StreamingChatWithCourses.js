import React, { useEffect, useState, useRef } from 'react';
import { useStreamingChat } from '../hooks/useStreamingChat';
import CourseCard from './CourseCard';
import { Send, MessageCircle, RefreshCw, User, Bot, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
import Course3DCarousel from './Course3DCarousel'

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
  const [showCourses, setShowCourses] = useState(true); // Show by default for demo
  const [copiedMessageId, setCopiedMessageId] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  // useEffect(() => {
  //   messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  // }, [messages]);

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
    const isStreamingMsg = isLast && message.message_type === 'assistant' && isStreaming;

    return (
      <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'} group`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-lg ${
          isUser 
            ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white' 
            : 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white'
        }`}>
          {isUser ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
        </div>

        {/* Message Content */}
        <div className={`flex flex-col max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
          {/* Message Bubble */}
          <div
            className={`px-6 py-4 rounded-2xl relative shadow-lg ${
              isUser
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-br-md'
                : 'bg-white text-gray-800 rounded-bl-md border border-gray-100'
            } ${isStreamingMsg ? 'animate-pulse' : ''}`}
          >
            {/* Message Text with better formatting */}
            <div className="whitespace-pre-wrap break-words leading-relaxed text-base">
              {message.content}
            </div>

            {/* Streaming indicator */}
            {isStreamingMsg && (
              <div className="flex items-center gap-2 mt-3 text-sm opacity-70">
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>AI is typing...</span>
              </div>
            )}
          </div>

          {/* Message Actions & Timestamp */}
          <div className={`flex items-center gap-3 mt-2 px-2 ${
            isUser ? 'flex-row-reverse' : 'flex-row'
          }`}>
            {/* Timestamp */}
            <span className="text-xs text-gray-400 font-medium">
              {message.timestamp ? formatTimestamp(message.timestamp) : 'Just now'}
            </span>

            {/* Action buttons (only for assistant messages) */}
            {!isUser && (
              <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => copyToClipboard(message.content, message.id)}
                  className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 hover:text-gray-700 transition-colors"
                  title="Copy message"
                >
                  <Copy className="h-4 w-4" />
                </button>
                <button
                  className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 hover:text-green-600 transition-colors"
                  title="Good response"
                >
                  <ThumbsUp className="h-4 w-4" />
                </button>
                <button
                  className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 hover:text-red-600 transition-colors"
                  title="Poor response"
                >
                  <ThumbsDown className="h-4 w-4" />
                </button>
              </div>
            )}

            {/* Copy confirmation */}
            {copiedMessageId === message.id && (
              <span className="text-xs text-green-600 animate-fade-in font-medium">
                Copied!
              </span>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-cyan-50 p-6">
      {/* <div className="max-w-[1400px] mx-auto"> */}
      <div className="max-w-7xl mx-auto space-y-8">

        {/* Main Layout - Now full width */}
        {/* <div className="grid lg:grid-cols-5 gap-8 h-[calc(100vh-3rem)]"> */}
          {/* Enhanced Chat Section - Takes 3 columns */}
          {/* <div className="lg:col-span-3 bg-white/80 backdrop-blur-sm rounded-2xl shadow-2xl overflow-hidden flex flex-col border border-white/20"> */}
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-2xl overflow-hidden flex flex-col border border-white/20 h-[70vh]">

            {/* Header */}
            <div className="bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-600 text-white p-8">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold flex items-center gap-3">
                    <MessageCircle className="h-7 w-7" />
                    AI Course Assistant
                  </h2>
                  <p className="text-purple-100 mt-2 text-lg">
                    {isConnected ? 'Connected - Ask me about courses!' : 'Connecting...'}
                  </p>
                </div>
                <button
                  onClick={resetChat}
                  className="p-3 hover:bg-white/10 rounded-xl transition-colors"
                  title="Reset chat"
                >
                  <RefreshCw className="h-6 w-6" />
                </button>
              </div>
            </div>

            {/* Status Bar */}
            {error && (
              <div className="bg-red-50 text-red-600 p-4 border-l-4 border-red-400">
                ⚠️ {error}
              </div>
            )}

            {/* Messages Container - Much larger */}
            {/* <div className="flex-1 overflow-y-auto p-8 space-y-8 min-h-[500px]"> */}
            <div className="flex-1 overflow-y-auto p-8 space-y-8">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
                  <div className="bg-gradient-to-r from-purple-100 to-blue-100 rounded-full p-8 mb-6">
                    <MessageCircle className="h-12 w-12 text-purple-500" />
                  </div>
                  <h3 className="text-2xl font-medium text-gray-700 mb-4">
                    Welcome! How can I help you today?
                  </h3>
                  <p className="text-gray-500 mb-6 text-lg">
                    I can answer questions, recommend courses, or just chat!
                  </p>
                  <div className="flex flex-wrap gap-3 justify-center">
                    {["Hello!", "I want to learn Python", "What's trending in tech?"].map((suggestion) => (
                      <button
                        key={suggestion}
                        onClick={() => setInputMessage(suggestion)}
                        className="px-4 py-2 bg-gradient-to-r from-purple-100 to-blue-100 hover:from-purple-200 hover:to-blue-200 rounded-full text-sm text-gray-700 transition-all transform hover:scale-105"
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
                    <div className="flex gap-4">
                      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white flex items-center justify-center shadow-lg">
                        <Bot className="h-5 w-5" />
                      </div>
                      <div className="bg-white text-gray-800 px-6 py-4 rounded-2xl rounded-bl-md shadow-lg border border-gray-100">
                        <div className="flex items-center gap-3">
                          <div className="flex gap-1">
                            <div className="w-3 h-3 bg-purple-400 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                            <div className="w-3 h-3 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                            <div className="w-3 h-3 bg-cyan-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                          </div>
                          <span className="text-sm text-gray-500 font-medium">AI is thinking...</span>
                        </div>
                      </div>
                    </div>
                  )}
                </>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Enhanced Input Section */}
            <div className="p-8 border-t bg-gradient-to-r from-gray-50 to-blue-50">
              <div className="flex gap-4">
                <div className="flex-1 relative">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask me anything or request courses..."
                    className="w-full px-6 py-4 border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none transition-all shadow-sm text-base"
                    disabled={!isConnected || isStreaming}
                    rows={Math.min(inputMessage.split('\n').length, 3)}
                    style={{ minHeight: '56px', maxHeight: '120px' }}
                  />
                  {inputMessage && (
                    <div className="absolute bottom-3 right-3 text-xs text-gray-400 font-medium">
                      {inputMessage.length}/1000
                    </div>
                  )}
                </div>
                <button
                  onClick={handleSendMessage}
                  disabled={!isConnected || isStreaming || !inputMessage.trim()}
                  className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-2xl hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3 transition-all hover:shadow-xl transform hover:scale-105"
                >
                  <Send className="h-5 w-5" />
                  <span className="hidden sm:inline font-medium">Send</span>
                </button>
              </div>
              
              {/* Connection status */}
              <div className="flex items-center justify-between mt-4">
                <div className="flex items-center gap-3 text-sm text-gray-500">
                  <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
                  <span className="font-medium">{isConnected ? 'Connected' : 'Disconnected'}</span>
                </div>
                <div className="text-sm text-gray-400">
                  Press Enter to send, Shift+Enter for new line
                </div>
              </div>
            </div>
          </div>

          {/* 3D Course Carousel Section - Takes 2 columns */}
          {/* <div className="lg:col-span-2 bg-white/80 backdrop-blur-sm rounded-2xl shadow-2xl overflow-hidden border border-white/20"> */}
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-2xl overflow-hidden border border-white/20 h-[100vh]">
            <div className="p-8 border-b bg-gradient-to-r from-purple-50 to-blue-50">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                📚 Course Recommendations
              </h2>
              <p className="text-gray-600 mt-2">Interactive 3D course showcase</p>
            </div>

            <div className="p-6">
              <Course3DCarousel 
                courses={courses}
                onAddToPlan={onAddToPlan}
                selectedCourses={selectedCourses}
              />
            </div>
          </div>
        </div>

        {/* Enhanced Quick Actions */}
        {showCourses ? (
          <div className="mt-8 text-center">
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-white/20">
              <p className="text-blue-800 mb-6 text-lg font-medium">
                💡 Try refining: "Actually, I want more advanced courses" or "Show me free options instead"
              </p>
              <div className="flex gap-4 justify-center flex-wrap">
                <button
                  onClick={() => sendMessage("Show me more advanced options")}
                  className="px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-2xl text-sm hover:from-blue-600 hover:to-cyan-600 transition-all transform hover:scale-105 shadow-lg font-medium"
                  disabled={isStreaming}
                >
                  More Advanced
                </button>
                <button
                  onClick={() => sendMessage("I need beginner-friendly courses")}
                  className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-2xl text-sm hover:from-green-600 hover:to-emerald-600 transition-all transform hover:scale-105 shadow-lg font-medium"
                  disabled={isStreaming}
                >
                  Beginner Level
                </button>
                <button
                  onClick={() => sendMessage("Find me free courses")}
                  className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-2xl text-sm hover:from-purple-600 hover:to-pink-600 transition-all transform hover:scale-105 shadow-lg font-medium"
                  disabled={isStreaming}
                >
                  Free Courses
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-8 text-center">
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-white/20">
              <p className="text-gray-600 mb-6 text-lg font-medium">
                💬 I can help with any question! Try asking about:
              </p>
              <div className="flex gap-4 justify-center flex-wrap">
                <button
                  onClick={() => sendMessage("What's the latest in AI technology?")}
                  className="px-6 py-3 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-2xl text-sm hover:from-gray-700 hover:to-gray-800 transition-all transform hover:scale-105 shadow-lg font-medium"
                  disabled={isStreaming}
                >
                  AI Technology
                </button>
                <button
                  onClick={() => sendMessage("I want to learn programming")}
                  className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-2xl text-sm hover:from-purple-600 hover:to-pink-600 transition-all transform hover:scale-105 shadow-lg font-medium"
                  disabled={isStreaming}
                >
                  Programming
                </button>
                <button
                  onClick={() => sendMessage("How can I improve my career?")}
                  className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-2xl text-sm hover:from-green-600 hover:to-emerald-600 transition-all transform hover:scale-105 shadow-lg font-medium"
                  disabled={isStreaming}
                >
                  Career Advice
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Custom CSS for 3D effects and animations */}
        <style jsx>{`
          @keyframes fade-in {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
          }
          .animate-fade-in {
            animation: fade-in 0.3s ease-in-out;
          }
          .perspective-1000 {
            perspective: 1000px;
          }
          .line-clamp-2 {
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
          .line-clamp-3 {
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
          .transform-style-preserve-3d {
            transform-style: preserve-3d;
          }
          
          /* Custom scrollbar */
          ::-webkit-scrollbar {
            width: 8px;
          }
          ::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 4px;
          }
          ::-webkit-scrollbar-thumb {
            background: linear-gradient(45deg, #8b5cf6, #ec4899);
            border-radius: 4px;
          }
          ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(45deg, #7c3aed, #db2777);
          }
        `}</style>
      </div>
    // </div>
  );
};

export default StreamingChatWithCourses;