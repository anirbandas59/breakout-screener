import React from 'react';

const Loader: React.FC = () => {
  return (
    <div className="flex justify-center items-center h-16">
      <div className="loader border-t-4 border-blue-500 rounded-full w-8 h-8 animate-spin"></div>
    </div>
  );
};

export default Loader;
