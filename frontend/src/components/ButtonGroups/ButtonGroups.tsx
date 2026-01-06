import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
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
    <div className="flex flex-col gap-4 mb-6" role="group" aria-label="Scanner controls">
      {/* Start/Stop/Clear Buttons */}
      <div className="flex gap-2" role="group" aria-label="Analysis controls">
        <Button
          onClick={handleStart}
          disabled={isGenerating}
          className="flex-1 bg-green-600 hover:bg-green-700 text-white"
          aria-label="Start breakout analysis"
        >
          {isGenerating && <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />}
          {isGenerating ? 'Generating...' : 'Start'}
        </Button>
        <Button
          onClick={handleStop}
          variant="destructive"
          className="flex-1"
          aria-label="Stop current analysis"
        >
          Stop
        </Button>
        <Button
          onClick={handleClear}
          disabled={isClearing}
          variant="outline"
          className="flex-1"
          aria-label="Clear chart data"
        >
          {isClearing && <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />}
          {isClearing ? 'Clearing...' : 'Clear'}
        </Button>
      </div>

      {/* Fetch List/Clear List Buttons */}
      <div className="flex gap-2" role="group" aria-label="Stock list controls">
        <Button
          disabled={isFetching}
          onClick={handleFetchList}
          className="flex-1 bg-green-600 hover:bg-green-700 text-white"
          aria-label="Fetch stock symbols from NSE"
        >
          {isFetching && <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />}
          {isFetching ? 'Fetching...' : 'Fetch List'}
        </Button>
        <Button
          disabled={isClearingList}
          onClick={handleClearList}
          variant="outline"
          className="flex-1"
          aria-label="Clear stock list"
        >
          {isClearingList && <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />}
          {isClearingList ? 'Clearing...' : 'Clear List'}
        </Button>
      </div>
    </div>
  );
};

export default ButtonGroups;
