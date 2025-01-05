import React, { useState } from 'react';
import { ButtonGroupsProps } from '@/types/AppInterfaces';

const ButtonGroups: React.FC<ButtonGroupsProps> = ({
  onStart,
  onStop,
  onClear,
  onFetchList,
  onClearList,
}) => {
  const [disabled, setDisabled] = useState(false);

  const handleStart = () => {
    onStart();
  };
  const handleStop = () => {
    onStop();
  };
  const handleClear = () => {
    onClear();
  };
  const handleFetchList = () => {
    setDisabled(true);
    onFetchList();
    setDisabled(false);
  };
  const handleClearList = () => {
    onClearList();
  };

  return (
    <div className="flex flex-col gap-4 mb-6">
      {/* Start/Stop/Clear Buttons */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-lg border border-gray-300">
        <button
          onClick={handleStart}
          className="flex-1 bg-gray-200 sm:text-xs text-sm font-semibold text-green-700 py-2 px-4 rounded-l-lg hover:text-gray-100 hover:bg-green-700"
        >
          Start
        </button>
        <button
          onClick={handleStop}
          className="flex-1 bg-gray-200 sm:text-xs text-sm font-semibold text-red-700 py-2 px-4 hover:text-gray-100 hover:bg-red-500"
        >
          Stop
        </button>
        <button
          onClick={handleClear}
          className="flex-1 bg-gray-200 sm:text-xs text-sm font-semibold text-gray-700 py-2 px-4 rounded-r-lg hover:bg-gray-300"
        >
          Clear
        </button>
      </div>

      {/* Fetch List/Clear List Buttons */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-lg border border-gray-300">
        <button
          disabled={disabled}
          onClick={handleFetchList}
          className="flex-1 bg-gray-200 sm:text-xs text-sm font-semibold text-green-700 py-2 px-4 rounded-l-lg hover:text-gray-100 hover:bg-green-700"
        >
          Fetch List
        </button>
        <button
          disabled={disabled}
          onClick={handleClearList}
          className="flex-1 bg-gray-200 sm:text-xs text-sm font-semibold text-gray-700 py-2 px-4 rounded-r-lg hover:bg-gray-300"
        >
          Clear List
        </button>
      </div>
    </div>
  );
};

export default ButtonGroups;
