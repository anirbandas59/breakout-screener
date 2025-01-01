'use client';

import React, { useState, useEffect, JSX } from 'react';

interface DataRow {
  group: string;
  //   sl_no: number;
  scripts: string;
  breakout: string;
  candle: string;
  volume: string;
  open: number;
  high: number;
  low: number;
  close: number;
  pdh: number;
  volume_today: number;
  cpr: number;
  res_1: number;
  res_2: number;
  supp_1: number;
  supp_2: number;
  narrow_gap: string;
  chart_link: string;
}

// Helper function to generate header cells
const generateHeaderRow = (columnName: string) => (
  <th key={columnName} className="text-left text-xs px-4 py-2 font-semibold border-r">
    {columnName}
  </th>
);

// Helper function to generate data cells
const generateDataCell = (value: string | number | JSX.Element, index: number) => (
  <td key={index} className="text-xs px-2 py-1 border-r">
    {value}
  </td>
);

const DataTable: React.FC = () => {
  const [data, setData] = useState<DataRow[]>([]);

  useEffect(() => {
    fetch('/test.json')
      .then((response) => response.json())
      .then((jsonData) => setData(jsonData))
      .catch((error) => console.error(`Error loading data: ${error}`));
  }, []);

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

  return (
    <div className="overflow-auto shadow-md rounded-lg">
      <table className="min-w-full bg-white border border-gray-300">
        <thead>
          <tr className="bg-blue-100 border-b">
            {columnHeaders.map((header) => generateHeaderRow(header))}
          </tr>
        </thead>
        <tbody>
          {data.map((row: DataRow, rowIndex: number) => (
            <tr
              key={rowIndex}
              className={`border-b ${rowIndex % 2 === 0 ? 'bg-gray-50' : 'bg-white'}`}
            >
              {[
                row.group,
                rowIndex + 1,
                row.scripts,
                row.breakout,
                row.candle,
                row.volume,
                row.open,
                row.high,
                row.low,
                row.close,
                row.pdh,
                row.volume_today,
                row.cpr,
                row.res_1,
                row.res_2,
                row.supp_1,
                row.supp_2,
                row.narrow_gap,
                <a
                  key={`chart_link_${row.scripts}`}
                  href={row.chart_link}
                  className="text-blue-500 hover:underline"
                >
                  View Chart
                </a>,
              ].map((cell, cellIndex) => generateDataCell(cell, cellIndex))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
