import React, { useState } from 'react';
import { useAtom } from 'jotai';
import { toast } from 'sonner';
import { Separator } from '@/components/ui/separator';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

import DisplayFields from '@/components/DisplayFields/DisplayFields';
import ButtonGroups from '@/components/ButtonGroups/ButtonGroups';
import {
  fetchScripts,
  generateBOData,
  clearChartData,
  clearCompleteData,
  suspendAction,
} from '@/services/api';
import {
  dateAtom,
  taskIdAtom,
  startTimeAtom,
  runningTimeAtom,
  scriptFetchedOnAtom,
  scriptsAnalyzedAtom,
} from '@/store/atoms';
import { formatDateTime } from '@/utils/helperFn';

const InputForm: React.FC = () => {
  const [date, setDate] = useAtom(dateAtom);
  const [, setTaskId] = useAtom(taskIdAtom);
  const [startTime] = useAtom(startTimeAtom);
  const [runningTime] = useAtom(runningTimeAtom);
  const [scriptFetchedOn] = useAtom(scriptFetchedOnAtom);
  const [scriptsAnalyzed] = useAtom(scriptsAnalyzedAtom);

  const [startFrom, setStartFrom] = useState(1);
  const [pivotGap, setPivotGap] = useState(0.5);

  // Handlers
  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setDate(e.target.value);
  };

  const handleStartFromChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setStartFrom(e.target.value ? parseInt(e.target.value) : 1);
  };

  const handleStart = async () => {
    try {
      const result = await generateBOData(date, pivotGap / 100, startFrom);
      setTaskId(result.task_id);
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
      setTaskId(result.task_id);
      toast.success('Clearing chart data...');
    } catch (error) {
      console.error(error);
      toast.error('Failed to clear chart data');
    }
  };

  const handleFetchList = async () => {
    try {
      const result = await fetchScripts();
      setTaskId(result.task_id);
      toast.success('Fetching stock list...');
    } catch (error) {
      console.error(error);
      toast.error('Failed to fetch stock list');
    }
  };

  const handleClearList = async () => {
    try {
      const result = await clearCompleteData();
      setTaskId(result.task_id);
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
    <div className="flex flex-col p-6">
      <div className="flex gap-6">
        {/* Left side: Input Fields & Button Groups */}
        <div className="flex-1 flex flex-col gap-4">
          {/* Input Fields - Side by side */}
          <div className="flex gap-4">
            <div className="flex-1">
              <Label htmlFor="date">Run Date</Label>
              <Input
                type="date"
                id="date"
                value={date}
                onChange={handleDateChange}
              />
            </div>
            <div className="flex-1">
              <Label htmlFor="startFrom">Start From</Label>
              <Input
                type="number"
                id="startFrom"
                value={startFrom}
                onChange={handleStartFromChange}
              />
            </div>
          </div>

          {/* Button Groups */}
          <ButtonGroups
            onStart={handleStart}
            onStop={handleStop}
            onClear={handleClear}
            onFetchList={handleFetchList}
            onClearList={handleClearList}
          />
        </div>

        {/* Vertical Separator */}
        <Separator orientation="vertical" className="h-auto" />

        {/* Right side: Display Fields */}
        <div className="flex-1">
          <div className="flex flex-col gap-2 mb-4">
            <span className="text-xl font-semibold">Stock Analysis</span>
            <Separator />
          </div>
          <DisplayFields
            scriptsAnalyzed={scriptsAnalyzed}
            startTime={formatDateTime(startTime)}
            runningTime={runningTime || '--:--:--'}
            fetchingTime={formatDateTime(scriptFetchedOn)}
            pivotGap={pivotGap}
            onPivotChange={handlePivotGap}
          />
        </div>
      </div>
    </div>
  );
};

export default InputForm;
