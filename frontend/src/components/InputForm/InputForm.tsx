import React, { useState } from 'react';
import { Divider } from '@mui/material';
import toast from 'react-hot-toast';

import DisplayFields from '@/components/DisplayFields/DisplayFields';
import ButtonGroups from '@/components/ButtonGroups/ButtonGroups';
import {
  fetchScripts,
  generateBOData,
  clearChartData,
  clearCompleteData,
  suspendAction,
} from '@/services/api';
import { InputFormProps } from '@/types/AppInterfaces';

const InputForm: React.FC<InputFormProps> = ({
  date,
  startTime,
  runningTime,
  scriptFetchedOn,
  scriptsAnalyzed,
  onTaskIdChange,
  onDateChange,
}) => {
  const [startFrom, setStartFrom] = useState(1);
  const [pivotGap, setPivotGap] = useState(0.5);

  // Handlers
  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    onDateChange(e.target.value);
  };

  const handleStartFromChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setStartFrom(e.target.value ? parseInt(e.target.value) : 1);
  };

  const handleStart = async () => {
    // Logic for starting analysis

    try {
      const result = await generateBOData(date, pivotGap / 100, startFrom);
      onTaskIdChange(result.task_id);
      toast.success('Analysis started!');
    } catch (error) {
      console.error(error);
      toast.error('Failed to start analysis');
    }
  };

  const handleStop = async () => {
    // Logic for stopping analysis
    try {
      const result = await suspendAction();
      console.log(result.message);
      toast.success('Analysis stopped');
    } catch (error) {
      console.error(error);
      toast.error('Failed to stop analysis');
    }
  };

  const handleClear = async () => {
    try {
      const result = await clearChartData();
      onTaskIdChange(result.task_id);
      toast.success('Clearing chart data...');
    } catch (error) {
      console.error(error);
      toast.error('Failed to clear chart data');
    }
  };

  const handleFetchList = async () => {
    try {
      const result = await fetchScripts();
      onTaskIdChange(result.task_id);
      toast.success('Fetching stock list...');
    } catch (error) {
      console.error(error);
      toast.error('Failed to fetch stock list');
    }
  };

  const handleClearList = async () => {
    try {
      const result = await clearCompleteData();
      onTaskIdChange(result.task_id);
      toast.success('Clearing complete data...');
    } catch (error) {
      console.error(error);
      toast.error('Failed to clear complete data');
    }
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
        runningTime={runningTime || '--:--:--'}
        fetchingTime={scriptFetchedOn || '--'}
        pivotGap={pivotGap}
        onPivotChange={handlePivotGap}
      />
    </div>
  );
};

export default InputForm;
