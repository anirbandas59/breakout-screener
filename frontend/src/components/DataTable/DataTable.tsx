'use client';

import React, { useEffect, JSX } from 'react';
import { useAtom } from 'jotai';
import Loader from '@/components/Loader/Loader';
import Pagination from '@/components/Pagination/Pagination';
import { DataRow } from '@/types/AppInterfaces';
import { getData } from '@/services/api';
import {
  tablePageAtom,
  tableLimitAtom,
  totalRecordsAtom,
  isLoadingAtom,
  startRefreshAtom,
  refreshTriggerAtom,
  scriptsAnalyzedAtom,
} from '@/store/atoms';

// Helper function to generate header cells
const generateHeaderRow = (columnName: string) => (
  <th key={columnName} className="text-left text-xs px-4 py-2 font-semibold border-r">
    {columnName}
  </th>
);

// Helper function to get indicator CSS class
const getIndicatorClass = (value: string | null | undefined, type: 'breakout' | 'candle' | 'volume'): string => {
  if (!value) return '';

  const normalized = value.toLowerCase().trim();

  if (type === 'breakout') {
    if (normalized === 'breakout') return 'indicator-breakout';
    if (normalized === 'red candle') return 'indicator-red-candle-breakout';
    if (normalized === 'no breakout') return 'indicator-no-breakout';
    if (normalized === 'big sell wick') return 'indicator-big-sell-wick';
    if (normalized === 'no entry') return 'indicator-no-entry';
  } else if (type === 'candle') {
    if (normalized === 'green candle') return 'indicator-green-candle';
    if (normalized === 'red candle') return 'indicator-red-candle';
    if (normalized === 'doji') return 'indicator-doji';
  } else if (type === 'volume') {
    if (normalized === 'good') return 'indicator-good';
    if (normalized === 'average') return 'indicator-average';
    if (normalized === 'low') return 'indicator-low';
  }

  return '';
};

// Helper function to generate data cells
const generateDataCell = (value: string | number | JSX.Element, index: number, className?: string) => (
  <td key={index} className={`text-xs px-2 py-1 border-r dark:text-white ${className || ''}`}>
    {value}
  </td>
);

const DataTable: React.FC = () => {
  const [page, setPage] = useAtom(tablePageAtom);
  const [limit, setLimit] = useAtom(tableLimitAtom);
  const [totalRecords, setTotalRecords] = useAtom(totalRecordsAtom);
  const [isLoading, setIsLoading] = useAtom(isLoadingAtom);
  const [startRefresh] = useAtom(startRefreshAtom);
  const [refreshTrigger] = useAtom(refreshTriggerAtom);
  const [, setScriptsAnalyzed] = useAtom(scriptsAnalyzedAtom);

  const [data, setData] = React.useState<DataRow[]>([]);

  const fetchData = async (page: number, limit: number) => {
    setIsLoading(true);

    try {
      const response = await getData(page, limit);
      const { total, data } = response;

      setData(data);
      setTotalRecords(total);
      setScriptsAnalyzed(total);
    } catch (error) {
      console.error('Error fetching error', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData(page, limit);
    console.log(startRefresh);

    if (startRefresh) {
      const interval = setInterval(() => {
        fetchData(page, limit);
      }, 10000); // Reduced from 30s to 10s for better sync with progress

      return () => clearInterval(interval);
    }
  }, [page, limit, startRefresh, refreshTrigger]); // Add refreshTrigger to trigger immediate refresh on task completion

  const columnHeaders = [
    'Group',
    'Sl. No',
    'Scripts',
    'Breakout',
    'Candle',
    'Volume Indicator',
    'Open',
    'High',
    'Low',
    'Close',
    'PDH',
    'Volume',
    'CPR',
    'RES-1',
    'RES-2',
    'SUPP-1',
    'SUPP-2',
    'Narrow Gap',
    'Chart Link',
  ];

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handleLimitChange = (newLimit: number) => {
    setLimit(newLimit);
    setPage(1);
  };

  return (
    <>
      <Pagination
        currentPage={page}
        totalPages={totalRecords}
        limit={limit}
        onPageChange={handlePageChange}
        onLimitChange={handleLimitChange}
      />
      <div className="overflow-auto shadow-md rounded-lg">
        {isLoading ? (
          <Loader />
        ) : data.length > 0 ? (
          <table className="min-w-full bg-white border border-gray-300">
            <thead>
              <tr className="bg-blue-100 dark:bg-gray-900 border-b">
                {columnHeaders.map((header) => generateHeaderRow(header))}
              </tr>
            </thead>
            <tbody>
              {data.map((row: DataRow, rowIndex: number) => (
                <tr
                  key={rowIndex}
                  className={`border-b ${
                    rowIndex % 2 === 0 ? 'bg-gray-50 dark:bg-gray-500' : 'bg-white dark:bg-gray-400'
                  }`}
                >
                  {generateDataCell(row.group_name, 0)}
                  {generateDataCell(rowIndex + 1 + (page - 1) * limit, 1)}
                  {generateDataCell(row.script_name, 2)}
                  <td className={`text-xs px-2 py-1 border-r ${getIndicatorClass(row.breakout_indicator, 'breakout')}`}>
                    {row.breakout_indicator}
                  </td>
                  <td className={`text-xs px-2 py-1 border-r ${getIndicatorClass(row.candle_indicator, 'candle')}`}>
                    {row.candle_indicator}
                  </td>
                  <td className={`text-xs px-2 py-1 border-r ${getIndicatorClass(row.volume_indicator, 'volume')}`}>
                    {row.volume_indicator}
                  </td>
                  {generateDataCell(row.open, 6)}
                  {generateDataCell(row.high, 7)}
                  {generateDataCell(row.low, 8)}
                  {generateDataCell(row.close, 9)}
                  {generateDataCell(row.previous_high, 10)}
                  {generateDataCell(row.volume, 11)}
                  {generateDataCell(row.cpr, 12)}
                  {generateDataCell(row.res1, 13)}
                  {generateDataCell(row.res2, 14)}
                  {generateDataCell(row.supp1, 15)}
                  {generateDataCell(row.supp2, 16)}
                  {generateDataCell(row.narrow_gap, 17)}
                  {generateDataCell(
                    <a
                      key={`chart_link_${row.script_name}`}
                      href={row.link}
                      target="_blank"
                      className="text-blue-600 dark:text-amber-200 dark:hover:text-amber-300 hover:underline hover:text-blue-700"
                    >
                      View Chart
                    </a>,
                    18
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="flex justify-center p-4 border border-gray-300 rounded-lg">
            <span className="dark:text-white text-sm sm:text-xs">No data to display &nbsp;</span>
          </div>
        )}
      </div>
    </>
  );
};

export default DataTable;
