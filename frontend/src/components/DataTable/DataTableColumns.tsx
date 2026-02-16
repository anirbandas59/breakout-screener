'use client';

import React, { useMemo } from 'react';
import { createColumnHelper, ColumnDef } from '@tanstack/react-table';
import { Filter } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { DataRow } from '@/types/AppInterfaces';
import {
  BREAKOUT_FILTER_OPTIONS,
  getIndicatorVariant,
} from '@/constants/indicators';

const columnHelper = createColumnHelper<DataRow>();

interface UseDataTableColumnsOptions {
  selectedBreakouts: string[];
  onBreakoutToggle: (value: string) => void;
  onClearFilters: () => void;
}

/**
 * Returns memoized column definitions for the breakout data table.
 * Wrapped in useMemo so columns are not recreated on every render.
 */
export function useDataTableColumns({
  selectedBreakouts,
  onBreakoutToggle,
  onClearFilters,
}: UseDataTableColumnsOptions): ColumnDef<DataRow, any>[] {
  return useMemo(
    () => [
      columnHelper.accessor('script_name', {
        header: 'Scripts',
        cell: (info) => <span className="text-xs font-medium">{info.getValue()}</span>,
      }),
      columnHelper.accessor('breakout_indicator', {
        header: () => (
          <div className="flex items-center gap-2">
            <span>Breakout</span>
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                  <Filter className="h-3 w-3" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-56" align="start">
                <div className="space-y-2">
                  <div className="font-semibold text-sm">Filter by Breakout</div>
                  {BREAKOUT_FILTER_OPTIONS.map((value) => (
                    <div key={value} className="flex items-center space-x-2">
                      <Checkbox
                        id={`breakout-${value}`}
                        checked={selectedBreakouts.includes(value)}
                        onCheckedChange={() => onBreakoutToggle(value)}
                      />
                      <label
                        htmlFor={`breakout-${value}`}
                        className="text-sm cursor-pointer flex-1"
                      >
                        {value}
                      </label>
                    </div>
                  ))}
                  {selectedBreakouts.length > 0 && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full mt-2"
                      onClick={onClearFilters}
                    >
                      Clear Filter
                    </Button>
                  )}
                </div>
              </PopoverContent>
            </Popover>
          </div>
        ),
        cell: (info) => (
          <Badge variant={getIndicatorVariant(info.getValue(), 'breakout')} className="text-xs">
            {info.getValue()}
          </Badge>
        ),
      }),
      columnHelper.accessor('candle_indicator', {
        header: 'Candle',
        cell: (info) => (
          <Badge variant={getIndicatorVariant(info.getValue(), 'candle')} className="text-xs">
            {info.getValue()}
          </Badge>
        ),
      }),
      columnHelper.accessor('volume_indicator', {
        header: 'Volume Indicator',
        cell: (info) => (
          <Badge variant={getIndicatorVariant(info.getValue(), 'volume')} className="text-xs">
            {info.getValue()}
          </Badge>
        ),
      }),
      columnHelper.accessor('open', {
        header: 'Open',
        cell: (info) => <span className="text-xs">{info.getValue()}</span>,
      }),
      columnHelper.accessor('high', {
        header: 'High',
        cell: (info) => <span className="text-xs">{info.getValue()}</span>,
      }),
      columnHelper.accessor('low', {
        header: 'Low',
        cell: (info) => <span className="text-xs">{info.getValue()}</span>,
      }),
      columnHelper.accessor('close', {
        header: 'Close',
        cell: (info) => <span className="text-xs">{info.getValue()}</span>,
      }),
      columnHelper.accessor('previous_high', {
        header: 'PDH',
        cell: (info) => <span className="text-xs">{info.getValue()}</span>,
      }),
      columnHelper.accessor('volume', {
        header: 'Volume',
        cell: (info) => <span className="text-xs">{info.getValue()}</span>,
      }),
      columnHelper.accessor('cpr', {
        header: 'CPR',
        cell: (info) => <span className="text-xs">{info.getValue()}</span>,
      }),
      columnHelper.accessor('res1', {
        header: 'RES-1',
        cell: (info) => <span className="text-xs">{info.getValue()}</span>,
      }),
      columnHelper.accessor('res2', {
        header: 'RES-2',
        cell: (info) => <span className="text-xs">{info.getValue()}</span>,
      }),
      columnHelper.accessor('supp1', {
        header: 'SUPP-1',
        cell: (info) => <span className="text-xs">{info.getValue()}</span>,
      }),
      columnHelper.accessor('supp2', {
        header: 'SUPP-2',
        cell: (info) => <span className="text-xs">{info.getValue()}</span>,
      }),
      columnHelper.accessor('narrow_gap', {
        header: 'Narrow Gap',
        cell: (info) => <span className="text-xs">{info.getValue()}</span>,
      }),
      columnHelper.accessor('link', {
        header: 'Chart Link',
        cell: (info) => (
          <a
            href={info.getValue()}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-blue-600 dark:text-amber-200 hover:underline dark:hover:text-amber-300"
          >
            View Chart
          </a>
        ),
      }),
    ],
    [selectedBreakouts, onBreakoutToggle, onClearFilters]
  );
}
