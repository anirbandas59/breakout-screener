import React, { useState } from 'react';
import { Divider } from '@mui/material';

import DisplayFields from '@/components/DisplayFields/DisplayFields';
import ButtonGroups from '@/components/ButtonGroups/ButtonGroups';
import { fetchScripts } from '@/services/api';
import { InputFormProps } from '@/types/AppInterfaces';

const InputForm: React.FC<InputFormProps> = ({
  date,
  onTaskIdChange,
  onDateChange,
  onStartRefresh,
}) => {
  // const [date, setDate] = useState('');
  const [startFrom, setStartFrom] = useState(1);
  const [scriptsAnalyzed, setScriptsAnalyzed] = useState(0);
  const [startTime, setStartTime] = useState<string>('');
  const [runningTime, setRunningTime] = useState<string>('');
  const [scriptFetchedOn, setScriptFetchedOn] = useState<string>('');
  const [pivotGap, setPivotGap] = useState(0);

  // Handlers
  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    onDateChange(e.target.value);
    // setDate(e.target.value);
    // console.log(e.target.value);
  };

  const handleStartFromChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setStartFrom(e.target.value ? parseInt(e.target.value) : 1);
  };

  const handleStart = () => {
    const now = new Date().toLocaleTimeString();
    onStartRefresh(true);
    setStartTime(now);
    console.log(`Refresh started at ${startTime}`);

    // Logic for starting analysis
  };

  const handleStop = () => {
    // Logic for stopping analysis
    onStartRefresh(false);
    console.log('Refresh stopped');
  };

  const handleClear = () => {
    onDateChange('');
    setStartFrom(1);
    setScriptsAnalyzed(0);
    setStartTime('');
    setRunningTime('');
    setScriptFetchedOn('');
    setPivotGap(0);
  };

  const handleFetchList = async () => {
    // let now: string;
    // onStartRefresh(true);
    try {
      const response = await fetchScripts();
      // now = new Date().toLocaleTimeString();

      console.log(`Generated response: ${response}`);
      onTaskIdChange(response.task_id);
    } catch (error) {
      console.error(error);
    } finally {
      const now = new Date().toLocaleTimeString();
      setScriptFetchedOn(now);
      // onStartRefresh(false);
    }
  };

  const handleClearList = () => {
    console.log('List is cleared');
  };

  const handlePivotGap = (value: number) => {
    setPivotGap(value);
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-100 dark:bg-gray-400 p-6">
      {/* Input Fields */}
      <div className="flex gap-4 mb-6 min-w-60">
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
      <ButtonGroups
        onStart={handleStart}
        onStop={handleStop}
        onClear={handleClear}
        onFetchList={handleFetchList}
        onClearList={handleClearList}
      />

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
        onPivotChange={handlePivotGap}
      />
    </div>
  );
};

export default InputForm;
