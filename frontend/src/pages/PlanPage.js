// PlanPage component
import React from 'react';
import { Target, BookOpen } from 'lucide-react';
import PlanItem from '../components/PlanItem';
import { calculateTotalStudyTime } from '../utils/helpers';

const PlanPage = ({ selectedCourses, onReorderPlan, onRemoveFromPlan, onFinalizePlan }) => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
          <Target className="h-6 w-6 mr-2 text-purple-500" />
          Your Learning Plan
        </h2>
        
        {selectedCourses.length === 0 ? (
          <div className="text-center py-12">
            <BookOpen className="h-16 w-16 mx-auto text-gray-300 mb-4" />
            <p className="text-gray-500">No courses selected yet. Go to Discover to find courses!</p>
            <button 
              onClick={() => window.location.hash = '#discover'}
              className="mt-4 bg-purple-500 text-white px-6 py-2 rounded-lg hover:bg-purple-600 transition-colors"
            >
              Start Exploring Courses
            </button>
          </div>
        ) : (
          <>
            <div className="bg-purple-50 p-4 rounded-lg mb-6">
              <h3 className="font-semibold text-purple-900 mb-2">📚 Your Personalized Learning Journey</h3>
              <p className="text-purple-700 text-sm">
                Courses are ordered by priority. You can reorder them to match your learning preferences and schedule.
              </p>
            </div>

            <div className="space-y-4 mb-6">
              {selectedCourses.map((course, index) => (
                <PlanItem
                  key={course.uuid}
                  course={course}
                  index={index}
                  totalCount={selectedCourses.length}
                  onReorder={onReorderPlan}
                  onRemove={onRemoveFromPlan}
                />
              ))}
            </div>
            
            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-600">
                Total estimated time: <span className="font-semibold">{calculateTotalStudyTime(selectedCourses)} hours</span>
              </div>
              <button
                onClick={onFinalizePlan}
                className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-2 rounded-lg hover:from-purple-600 hover:to-pink-600 transition-colors font-medium"
              >
                Finalize Study Plan
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default PlanPage;