import React, { useState } from 'react';
import DisplayFields from '@/components/DisplayFields/DisplayFields';
import { Divider } from '@mui/material';

const InputForm: React.FC = () => {
  const [date, setDate] = useState('');
  const [startFrom, setStartFrom] = useState<number>(1);
  const [scriptsAnalyzed, setScriptsAnalyzed] = useState<number>(0);
  const [startTime, setStartTime] = useState<string>('');
  const [runningTime, setRunningTime] = useState<string>('');
  const [scriptFetchedOn, setScriptFetchedOn] = useState<string>('');
  const [pivotGap, setPivotGap] = useState<number>(0);

  // Handlers
  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setDate(e.target.value);
    // console.log(e.target.value);
  };

  const handleStartFromChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setStartFrom(e.target.value ? parseInt(e.target.value) : 1);
  };

  const handleStart = () => {
    setStartTime(new Date().toLocaleTimeString());
    // Logic for starting analysis
  };

  const handleStop = () => {
    // Logic for stopping analysis
  };

  const handleClear = () => {
    setDate('');
    setStartFrom(1);
    setScriptsAnalyzed(0);
    setStartTime('');
    setRunningTime('');
    setScriptFetchedOn('');
    setPivotGap(0);
  };

  const handleFetchList = () => {
    setScriptFetchedOn(new Date().toLocaleString());
  };

  const handleClearList = () => {
    console.log('List is cleared');
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-100 dark:bg-gray-400 p-6">
      {/* Input Fields */}
      <div className="flex gap-4 mb-6">
        <div className="flex-1">
          <label className="block font-medium sm:text-xs text-sm mb-2" htmlFor="date">
            Run Date
          </label>
          <input
            type="date"
            id="date"
            value={date}
            onChange={handleDateChange}
            className="w-full sm:p-2 p-3 border border-gray-300  rounded sm:text-xs text-sm dark:text-gray-500"
          />
        </div>
        <div className="flex-1">
          <label className="block sm:text-xs text-sm font-medium mb-2" htmlFor="startFrom">
            Start From
          </label>
          <input
            type="number"
            id="startFrom"
            value={startFrom}
            onChange={handleStartFromChange}
            className="w-full sm:p-2 p-3 border border-gray-300 rounded sm:text-xs text-sm dark:text-gray-500"
          />
        </div>
      </div>

      {/* Buttons */}
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
            onClick={handleFetchList}
            className="flex-1 bg-gray-200 sm:text-xs text-sm font-semibold text-green-700 py-2 px-4 rounded-l-lg hover:text-gray-100 hover:bg-green-700"
          >
            Fetch List
          </button>
          <button
            onClick={handleClearList}
            className="flex-1 bg-gray-200 sm:text-xs text-sm font-semibold text-gray-700 py-2 px-4 rounded-r-lg hover:bg-gray-300"
          >
            Clear List
          </button>
        </div>
      </div>

      {/* Text with Divider */}
      <div className="flex flex-col gap-2 mb-6">
        <span className="text-xl">Stock Analysis</span>
        <Divider />
      </div>

      {/* Read-Only Fields */}
      <DisplayFields
        scriptsAnalyzed={scriptsAnalyzed}
        startTime={startTime}
        runningTime={runningTime}
        fetchingTime={scriptFetchedOn}
        pivotGap={pivotGap}
      />
    </div>
  );
};

export default InputForm;
