'use client';

import React, { useState, useEffect, JSX } from 'react';
import Loader from '@/components/Loader/Loader';
import Pagination from '@/components/Pagination/Pagination';
import { DataRow, DataTableProps } from '@/types/AppInterfaces';
import { getData } from '@/services/api';

// Helper function to generate header cells
const generateHeaderRow = (columnName: string) => (
  <th key={columnName} className="text-left text-xs px-4 py-2 font-semibold border-r">
    {columnName}
  </th>
);

// Helper function to generate data cells
const generateDataCell = (value: string | number | JSX.Element, index: number) => (
  <td key={index} className="text-xs px-2 py-1 border-r dark:text-white">
    {value}
  </td>
);

const DataTable: React.FC<DataTableProps> = ({ date, startRefresh }) => {
  const [data, setData] = useState<DataRow[]>([]);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(30);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const fetchData = async (page: number, limit: number) => {
    setIsLoading(true);

    try {
      const response = await getData(page, limit);

      // console.log(response.data);
      const { total, data } = response;

      setData(data);
      setTotalPages(total);
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
      }, 30000);

      return () => clearInterval(interval);
    }
  }, [page, limit, startRefresh]);

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
        date={date}
        currentPage={page}
        totalPages={totalPages}
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
                  {[
                    row.group_name,
                    rowIndex + 1 + (page - 1) * limit,
                    // row.id,
                    row.script_name,
                    row.breakout_indicator,
                    row.candle_indicator,
                    row.volume_indicator,
                    row.open,
                    row.high,
                    row.low,
                    row.close,
                    row.previous_high,
                    row.volume,
                    row.cpr,
                    row.res1,
                    row.res2,
                    row.supp1,
                    row.supp2,
                    row.narrow_gap,
                    <a
                      key={`chart_link_${row.script_name}`}
                      href={row.link}
                      target="_blank"
                      className="text-blue-600 dark:text-amber-200 dark:hover:text-amber-300 hover:underline hover:text-blue-700"
                    >
                      View Chart
                    </a>,
                  ].map((cell, cellIndex) => generateDataCell(cell, cellIndex))}
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
