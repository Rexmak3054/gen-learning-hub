import React, { useState } from 'react';
import './index.css';

// Simple course search component
function CourseSearch() {
  const [query, setQuery] = useState('');
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);

  const searchCourses = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch('/api/search-courses', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, k: 5 }),
      });
      
      const data = await response.json();
      setCourses(data.courses || []);
    } catch (error) {
      console.error('Search failed:', error);
      setCourses([]);
    }
    setLoading(false);
  };

  const quickSearch = (topic) => {
    setQuery(topic);
    setTimeout(() => searchCourses(), 100);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          🎓 Grace Papers Gen
        </h1>
        <p className="text-xl text-gray-600">
          AI-Powered Learning Platform
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex gap-4 mb-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What would you like to learn?"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyPress={(e) => e.key === 'Enter' && searchCourses()}
          />
          <button
            onClick={searchCourses}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>

        <div className="grid gap-4">
          {courses.map((course) => (
            <div key={course.uuid} className="border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {course.title}
              </h3>
              <p className="text-gray-600 mb-2">{course.description}</p>
              <div className="flex gap-2 text-sm text-gray-500">
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                  {course.provider}
                </span>
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded">
                  {course.level}
                </span>
              </div>
            </div>
          ))}
        </div>

        {courses.length === 0 && !loading && (
          <div className="text-center text-gray-500 mt-8">
            <p>Search for courses to get started!</p>
          </div>
        )}
      </div>

      <div className="bg-gray-50 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Popular Topics</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            'Python Programming',
            'Data Science',
            'Machine Learning', 
            'AI Tools',
            'Excel Automation',
            'Digital Marketing',
            'Project Management',
            'Business Analysis'
          ].map((topic) => (
            <button
              key={topic}
              onClick={() => quickSearch(topic)}
              className="p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow text-center text-gray-700 hover:text-blue-600"
            >
              {topic}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-8 text-center text-gray-500">
        <p>🚀 Deployed with Vercel + AWS Integration Ready</p>
      </div>
    </div>
  );
}

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <CourseSearch />
    </div>
  );
}

export default App;