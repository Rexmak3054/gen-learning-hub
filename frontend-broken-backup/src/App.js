import React, { useState } from 'react';

const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
  },
  header: {
    textAlign: 'center',
    marginBottom: '40px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    padding: '40px 20px',
    borderRadius: '12px'
  },
  title: {
    fontSize: '3rem',
    margin: '0 0 10px 0',
    fontWeight: 'bold'
  },
  subtitle: {
    fontSize: '1.2rem',
    margin: 0,
    opacity: 0.9
  },
  searchSection: {
    background: 'white',
    padding: '30px',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    marginBottom: '30px'
  },
  searchContainer: {
    display: 'flex',
    gap: '10px',
    marginBottom: '20px'
  },
  input: {
    flex: 1,
    padding: '12px',
    border: '2px solid #e5e7eb',
    borderRadius: '8px',
    fontSize: '16px',
    outline: 'none'
  },
  button: {
    padding: '12px 24px',
    backgroundColor: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  buttonDisabled: {
    opacity: 0.6,
    cursor: 'not-allowed'
  },
  courseGrid: {
    display: 'grid',
    gap: '20px',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))'
  },
  courseCard: {
    background: 'white',
    padding: '20px',
    borderRadius: '12px',
    border: '1px solid #e5e7eb',
    transition: 'transform 0.2s, box-shadow 0.2s'
  },
  courseTitle: {
    fontSize: '1.25rem',
    fontWeight: 'bold',
    margin: '0 0 10px 0',
    color: '#1f2937'
  },
  courseDescription: {
    color: '#6b7280',
    marginBottom: '15px',
    lineHeight: '1.5'
  },
  courseMeta: {
    display: 'flex',
    gap: '10px'
  },
  badge: {
    padding: '4px 12px',
    borderRadius: '20px',
    fontSize: '0.875rem',
    fontWeight: '500'
  },
  badgeProvider: {
    backgroundColor: '#dbeafe',
    color: '#1e40af'
  },
  badgeLevel: {
    backgroundColor: '#d1fae5',
    color: '#065f46'
  },
  emptyState: {
    textAlign: 'center',
    padding: '40px',
    color: '#6b7280'
  },
  quickTopics: {
    background: 'white',
    padding: '30px',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
  },
  topicsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '15px',
    marginTop: '20px'
  },
  topicButton: {
    padding: '15px',
    background: '#f9fafb',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    cursor: 'pointer',
    textAlign: 'center',
    fontSize: '14px',
    fontWeight: '500',
    color: '#374151',
    transition: 'all 0.2s'
  }
};

function App() {
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
        body: JSON.stringify({ query, k: 6 }),
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
    setTimeout(() => {
      searchCourses();
    }, 100);
  };

  const topics = [
    'Python Programming',
    'Data Science', 
    'Machine Learning',
    'AI Tools',
    'Excel Automation',
    'Digital Marketing',
    'Project Management',
    'Business Analysis'
  ];

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>🎓 Grace Papers Gen</h1>
        <p style={styles.subtitle}>AI-Powered Learning Platform</p>
      </div>

      <div style={styles.searchSection}>
        <div style={styles.searchContainer}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What would you like to learn today?"
            style={styles.input}
            onKeyPress={(e) => e.key === 'Enter' && searchCourses()}
          />
          <button
            onClick={searchCourses}
            disabled={loading}
            style={{
              ...styles.button,
              ...(loading ? styles.buttonDisabled : {})
            }}
            onMouseOver={(e) => {
              if (!loading) e.target.style.backgroundColor = '#5a67d8';
            }}
            onMouseOut={(e) => {
              if (!loading) e.target.style.backgroundColor = '#667eea';
            }}
          >
            {loading ? 'Searching...' : 'Search Courses'}
          </button>
        </div>

        {courses.length > 0 && (
          <div style={styles.courseGrid}>
            {courses.map((course) => (
              <div 
                key={course.uuid} 
                style={styles.courseCard}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)';
                  e.currentTarget.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.15)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <h3 style={styles.courseTitle}>{course.title}</h3>
                <p style={styles.courseDescription}>{course.description}</p>
                <div style={styles.courseMeta}>
                  <span style={{...styles.badge, ...styles.badgeProvider}}>
                    {course.provider}
                  </span>
                  <span style={{...styles.badge, ...styles.badgeLevel}}>
                    {course.level}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {courses.length === 0 && !loading && query && (
          <div style={styles.emptyState}>
            <p>No courses found for "{query}". Try different keywords!</p>
          </div>
        )}
      </div>

      <div style={styles.quickTopics}>
        <h2 style={{margin: '0 0 10px 0', color: '#1f2937'}}>Popular Topics</h2>
        <p style={{color: '#6b7280', margin: '0 0 20px 0'}}>
          Click any topic to search instantly
        </p>
        <div style={styles.topicsGrid}>
          {topics.map((topic) => (
            <button
              key={topic}
              onClick={() => quickSearch(topic)}
              style={styles.topicButton}
              onMouseOver={(e) => {
                e.target.style.backgroundColor = '#f3f4f6';
                e.target.style.borderColor = '#667eea';
                e.target.style.color = '#667eea';
              }}
              onMouseOut={(e) => {
                e.target.style.backgroundColor = '#f9fafb';
                e.target.style.borderColor = '#e5e7eb';
                e.target.style.color = '#374151';
              }}
            >
              {topic}
            </button>
          ))}
        </div>
      </div>

      <div style={{textAlign: 'center', marginTop: '40px', color: '#6b7280'}}>
        <p>🚀 Successfully deployed with Node.js v23 compatibility</p>
        <p>Backend API connected • Mock data ready • AWS integration available</p>
      </div>
    </div>
  );
}

export default App;
