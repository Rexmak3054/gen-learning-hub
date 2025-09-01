// ProfilePage component
import React from 'react';
import { Calendar, CheckCircle, Trophy, Clock, Target } from 'lucide-react';
import { generateUserInitials } from '../utils/helpers';

const ProfilePage = ({ userProfile, studyPlan }) => {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Profile Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl p-8 mb-8 text-white">
        <div className="flex items-center mb-6">
          <div className="h-20 w-20 bg-white/20 rounded-full flex items-center justify-center text-2xl font-bold mr-6">
            {generateUserInitials(userProfile.name)}
          </div>
          <div>
            <h1 className="text-3xl font-bold mb-2">{userProfile.name}</h1>
            <p className="text-purple-100 text-lg">{userProfile.role}</p>
            <p className="text-purple-200 text-sm">Experience Level: {userProfile.experience}</p>
          </div>
        </div>
        
        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold mb-1">{userProfile.completedCourses}</div>
            <div className="text-purple-100">Courses Completed</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold mb-1">{userProfile.totalHours}</div>
            <div className="text-purple-100">Hours Learned</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold mb-1">{studyPlan.length}</div>
            <div className="text-purple-100">Planned Courses</div>
          </div>
        </div>
      </div>

      {/* Current Study Plan */}
      {studyPlan.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <Calendar className="h-6 w-6 mr-2 text-purple-500" />
            Your Active Study Plan
          </h2>
          
          <div className="space-y-4">
            {studyPlan.map((course, index) => (
              <div key={course.uuid} className="flex items-center bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors">
                <div className="bg-purple-500 text-white rounded-full h-8 w-8 flex items-center justify-center font-bold mr-4">
                  {index + 1}
                </div>
                
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900">{course.title}</h4>
                  <p className="text-sm text-gray-600">{course.partner_primary} • {course.duration}</p>
                  <div className="flex items-center mt-1">
                    <Clock className="h-3 w-3 mr-1 text-gray-400" />
                    <span className="text-xs text-gray-500">{course.effort}</span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <span className="text-sm text-gray-500 bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full">
                    Not Started
                  </span>
                  <button 
                    className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors text-sm font-medium"
                    onClick={() => window.open(course.url, '_blank')}
                  >
                    Start Course
                  </button>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 p-4 bg-green-50 rounded-lg">
            <div className="flex items-center">
              <Trophy className="h-5 w-5 text-green-600 mr-2" />
              <span className="text-green-800 font-medium">Ready to start your AI learning journey!</span>
            </div>
          </div>
        </div>
      )}

      {/* Learning Goals */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <Target className="h-6 w-6 mr-2 text-purple-500" />
          Learning Goals
        </h2>
        <div className="grid md:grid-cols-3 gap-4">
          {userProfile.goals.map((goal, index) => (
            <div key={index} className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-purple-300 transition-colors">
              <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
              <span className="font-medium text-gray-900">{goal}</span>
            </div>
          ))}
        </div>
        
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">🎯 Why AI Skills Matter for Women</h3>
          <p className="text-blue-700 text-sm">
            Research shows that women are 50% less likely to use AI tools in the workplace. 
            By developing these skills, you're positioning yourself at the forefront of the future of work!
          </p>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;