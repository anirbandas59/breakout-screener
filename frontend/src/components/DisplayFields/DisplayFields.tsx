'use client';

import * as React from 'react';

interface ReadOnlyFieldsProps {
  scriptsAnalyzed: number;
  startTime: string;
  runningTime: string;
  fetchingTime: string;
  pivotGap: number;
}

const DisplayFields: React.FC<ReadOnlyFieldsProps> = ({
  scriptsAnalyzed,
  startTime,
  runningTime,
  fetchingTime,
  pivotGap,
}) => {
  return (
    <div className="bg-yellow-100 rounded p-4 shadow-md w-full">
      <div className="mb-2 flex justify-between">
        <span className="text-sm sm:text-xs font-medium">Scripts Analyzed:</span>
        <span className="text-sm sm:text-xs text-blue-500">{scriptsAnalyzed}</span>
      </div>
      <div className="mb-2 flex justify-between">
        <span className="text-sm sm:text-xs font-medium">Start Time:</span>
        <span className="text-sm sm:text-xs text-blue-500">{startTime || '--'}</span>
      </div>
      <div className="mb-2 flex justify-between">
        <span className="font-medium text-sm sm:text-xs">Running Time:</span>
        <span className="text-blue-500 text-sm sm:text-xs">{runningTime || '--'}</span>
      </div>
      <div className="mb-2 flex justify-between">
        <span className="font-medium text-sm sm:text-xs">Script Fetched On:</span>
        <span className="text-blue-500 text-sm sm:text-xs">{fetchingTime || '--'}</span>
      </div>
      <div className="mb-2 flex justify-between">
        <span className="font-medium text-sm sm:text-xs">Pivot %:</span>
        <span className="text-blue-500 text-sm sm:text-xs">{pivotGap}</span>
      </div>
    </div>
  );
};

export default DisplayFields;
