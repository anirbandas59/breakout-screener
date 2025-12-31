import Papa from 'papaparse';
import { DataRow } from '@/types/AppInterfaces';

export const exportToCSV = (data: DataRow[], filename: string = 'breakout_data.csv') => {
  if (!data || data.length === 0) {
    console.warn('No data to export');
    return;
  }

  // Transform data to include all fields in desired order
  const csvData = data.map((row) => ({
    'Group': row.group_name,
    'Script Name': row.script_name,
    'Date': row.date,
    'Breakout Indicator': row.breakout_indicator,
    'Candle Indicator': row.candle_indicator,
    'Volume Indicator': row.volume_indicator,
    'Open': row.open,
    'High': row.high,
    'Low': row.low,
    'Close': row.close,
    'Previous High': row.previous_high,
    'Volume': row.volume,
    'CPR': row.cpr,
    'RES-1': row.res1,
    'RES-2': row.res2,
    'SUPP-1': row.supp1,
    'SUPP-2': row.supp2,
    'Narrow Gap': row.narrow_gap,
    'Chart Link': row.link,
  }));

  const csv = Papa.unparse(csvData, {
    header: true,
  });

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);

  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};
