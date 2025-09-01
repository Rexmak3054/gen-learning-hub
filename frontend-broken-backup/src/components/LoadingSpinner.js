// LoadingSpinner component
import React from 'react';

const LoadingSpinner = ({ message = "Loading..." }) => {
  return (
    <div className="text-center py-12">
      <div className="inline-flex items-center px-6 py-3 bg-purple-50 rounded-full">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-500 mr-3"></div>
        <span className="text-purple-700 font-medium">{message}</span>
      </div>
    </div>
  );
};

export default LoadingSpinner;