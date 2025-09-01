// PlanItem component
import React from 'react';

const PlanItem = ({ course, index, totalCount, onReorder, onRemove }) => {
  return (
    <div className="flex items-center bg-gray-50 rounded-lg p-4">
      <div className="bg-purple-500 text-white rounded-full h-8 w-8 flex items-center justify-center font-bold mr-4">
        {course.priority}
      </div>
      
      <div className="flex-1">
        <h4 className="font-semibold text-gray-900">{course.title}</h4>
        <p className="text-sm text-gray-600">{course.partner_primary} • {course.duration}</p>
      </div>
      
      <div className="flex items-center space-x-2">
        <button
          onClick={() => onReorder(course.uuid, 'up')}
          disabled={index === 0}
          className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50"
        >
          ↑
        </button>
        <button
          onClick={() => onReorder(course.uuid, 'down')}
          disabled={index === totalCount - 1}
          className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50"
        >
          ↓
        </button>
        <button
          onClick={() => onRemove(course.uuid)}
          className="p-1 text-red-400 hover:text-red-600"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

export default PlanItem;