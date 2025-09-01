import React, { useState } from 'react';
import Navigation from './components/Navigation';
import EnhancedDiscoverPage from './pages/EnhancedDiscoverPage';
import PlanPage from './pages/PlanPage';
import ProfilePage from './pages/ProfilePage';
import useCourseManager from './hooks/useCourseManager';

function App() {
  const [currentView, setCurrentView] = useState('discover'); // discover, plan, profile
  const [userProfile] = useState({
    id: 'user-123',
    name: 'Sarah Chen',
    role: 'Marketing Manager',
    experience: 'Beginner',
    goals: ['AI Tools Proficiency', 'Data Analysis', 'Automation'],
    completedCourses: 3,
    totalHours: 24
  });

  const {
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
  } = useCourseManager();

  const handleFinalizePlan = () => {
    finalizePlan();
    setCurrentView('profile');
  };

  const renderCurrentPage = () => {
    switch (currentView) {
      case 'discover':
        return (
          <EnhancedDiscoverPage
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            recommendations={recommendations}
            isSearching={isSearching}
            onSearch={searchCourses}
            onAddToPlan={addToPlan}
            selectedCourses={selectedCourses}
          />
        );
      case 'plan':
        return (
          <PlanPage
            selectedCourses={selectedCourses}
            onReorderPlan={reorderPlan}
            onRemoveFromPlan={removeFromPlan}
            onFinalizePlan={handleFinalizePlan}
          />
        );
      case 'profile':
        return (
          <ProfilePage
            userProfile={userProfile}
            studyPlan={studyPlan}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation 
        currentView={currentView}
        setCurrentView={setCurrentView}
        selectedCoursesCount={selectedCourses.length}
      />
      
      <main className="py-8 px-6">
        {renderCurrentPage()}
      </main>
    </div>
  );
}

export default App;