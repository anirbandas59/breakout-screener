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
    <div className="flex flex-col gap-4 mb-6">
      {/* Start/Stop/Clear Buttons */}
      <div className="flex gap-2">
        <Button
          onClick={handleStart}
          disabled={isGenerating}
          className="flex-1 bg-green-600 hover:bg-green-700 text-white"
        >
          {isGenerating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {isGenerating ? 'Generating...' : 'Start'}
        </Button>
        <Button
          onClick={handleStop}
          variant="destructive"
          className="flex-1"
        >
          Stop
        </Button>
        <Button
          onClick={handleClear}
          disabled={isClearing}
          variant="outline"
          className="flex-1"
        >
          {isClearing && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {isClearing ? 'Clearing...' : 'Clear'}
        </Button>
      </div>

      {/* Fetch List/Clear List Buttons */}
      <div className="flex gap-2">
        <Button
          disabled={isFetching}
          onClick={handleFetchList}
          className="flex-1 bg-green-600 hover:bg-green-700 text-white"
        >
          {isFetching && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {isFetching ? 'Fetching...' : 'Fetch List'}
        </Button>
        <Button
          disabled={isClearingList}
          onClick={handleClearList}
          variant="outline"
          className="flex-1"
        >
          {isClearingList && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {isClearingList ? 'Clearing...' : 'Clear List'}
        </Button>
      </div>
    </div>
  );
};

export default ButtonGroups;
