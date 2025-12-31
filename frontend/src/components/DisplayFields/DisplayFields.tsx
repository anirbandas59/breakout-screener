'use client';

import * as React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

interface ReadOnlyFieldsProps {
  scriptsAnalyzed: number;
  startTime: string;
  runningTime: string;
  fetchingTime: string;
  pivotGap: number;
  onPivotChange: (value: number) => void;
}

const DisplayFields: React.FC<ReadOnlyFieldsProps> = ({
  scriptsAnalyzed,
  startTime,
  runningTime,
  fetchingTime,
  pivotGap,
  onPivotChange,
}) => {
  const handlePivotChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const newValue = parseFloat(e.target.value);
    if (!Number.isNaN(newValue)) {
      onPivotChange(newValue);
    }
  };

  return (
    <Card>
      <CardContent className="pt-6 space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium">Scripts Analyzed:</span>
          <span className="text-sm text-primary">{scriptsAnalyzed}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium">Start Time:</span>
          <span className="text-sm text-muted-foreground">
            {startTime || '--'}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium">Running Time:</span>
          <span className="text-sm text-muted-foreground">{runningTime || '--'}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium">Script Fetched On:</span>
          <span className="text-sm text-muted-foreground">
            {fetchingTime || '--'}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium">Pivot %:</span>
          <Input
            type="number"
            value={pivotGap}
            onChange={handlePivotChange}
            className="w-20 h-8"
          />
        </div>
      </CardContent>
    </Card>
  );
};

export default DisplayFields;
