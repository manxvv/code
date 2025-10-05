import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="flex flex-1 justify-center items-center h-full">
      <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
    </div>
  );
};

export default LoadingSpinner;