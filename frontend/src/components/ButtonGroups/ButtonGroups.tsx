import React, { useState } from 'react';
import { ButtonGroupsProps } from '@/types/AppInterfaces';

const ButtonGroups: React.FC<ButtonGroupsProps> = ({
  onStart,
  onStop,
  onClear,
  onFetchList,
  onClearList,
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const [isClearing, setIsClearing] = useState(false);
  const [isClearingList, setIsClearingList] = useState(false);

  const handleStart = async () => {
    setIsGenerating(true);
    try {
      await onStart();
    } finally {
      setIsGenerating(false);
    }
  };

  const handleStop = () => {
    onStop();
  };

  const handleClear = async () => {
    setIsClearing(true);
    try {
      await onClear();
    } finally {
      setIsClearing(false);
    }
  };

  const handleFetchList = async () => {
    setIsFetching(true);
    try {
      await onFetchList();
    } finally {
      setIsFetching(false);
    }
  };

  const handleClearList = async () => {
    setIsClearingList(true);
    try {
      await onClearList();
    } finally {
      setIsClearingList(false);
    }
  };

  return (
    <div className="flex flex-col gap-4 mb-6">
      {/* Start/Stop/Clear Buttons */}
      <div className="flex gap-1 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg border border-gray-300 dark:border-gray-600">
        <button
          onClick={handleStart}
          disabled={isGenerating}
          className="flex-1 bg-gray-200 dark:bg-gray-600 sm:text-xs text-sm font-semibold text-green-700 dark:text-green-400 py-2 px-4 rounded-l-lg hover:text-gray-100 hover:bg-green-700 dark:hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isGenerating && (
            <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
          {isGenerating ? 'Generating...' : 'Start'}
        </button>
        <button
          onClick={handleStop}
          className="flex-1 bg-gray-200 dark:bg-gray-600 sm:text-xs text-sm font-semibold text-red-700 dark:text-red-400 py-2 px-4 hover:text-gray-100 hover:bg-red-500 dark:hover:bg-red-600"
        >
          Stop
        </button>
        <button
          onClick={handleClear}
          disabled={isClearing}
          className="flex-1 bg-gray-200 dark:bg-gray-600 sm:text-xs text-sm font-semibold text-gray-700 dark:text-gray-300 py-2 px-4 rounded-r-lg hover:bg-gray-300 dark:hover:bg-gray-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isClearing && (
            <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
          {isClearing ? 'Clearing...' : 'Clear'}
        </button>
      </div>

      {/* Fetch List/Clear List Buttons */}
      <div className="flex gap-1 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg border border-gray-300 dark:border-gray-600">
        <button
          disabled={isFetching}
          onClick={handleFetchList}
          className="flex-1 bg-gray-200 dark:bg-gray-600 sm:text-xs text-sm font-semibold text-green-700 dark:text-green-400 py-2 px-4 rounded-l-lg hover:text-gray-100 hover:bg-green-700 dark:hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isFetching && (
            <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
          {isFetching ? 'Fetching...' : 'Fetch List'}
        </button>
        <button
          disabled={isClearingList}
          onClick={handleClearList}
          className="flex-1 bg-gray-200 dark:bg-gray-600 sm:text-xs text-sm font-semibold text-gray-700 dark:text-gray-300 py-2 px-4 rounded-r-lg hover:bg-gray-300 dark:hover:bg-gray-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isClearingList && (
            <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
          {isClearingList ? 'Clearing...' : 'Clear List'}
        </button>
      </div>
    </div>
  );
};

export default ButtonGroups;
