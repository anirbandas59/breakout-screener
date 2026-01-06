'use client';

import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { Calendar as CalendarIcon, Download } from 'lucide-react';
import { DateRange } from 'react-day-picker';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Badge } from '@/components/ui/badge';
import { getData } from '@/services/api';
import { DataRow } from '@/types/AppInterfaces';
import { exportToCSV } from '@/utils/csvExport';
import { cn } from '@/lib/utils';

export default function Reports() {
  const [date, setDate] = useState<DateRange | undefined>({
    from: new Date(),
    to: new Date(),
  });
  const [isLoading, setIsLoading] = useState(false);
  const [historicalData, setHistoricalData] = useState<DataRow[]>([]);
  const [stats, setStats] = useState({
    totalBreakouts: 0,
    totalScripts: 0,
    avgVolume: 0,
  });

  // Calculate statistics from data
  useEffect(() => {
    if (historicalData.length > 0) {
      const breakoutCount = historicalData.filter(
        (item) => item.breakout_indicator === 'BREAKOUT'
      ).length;
      const totalScripts = new Set(historicalData.map((item) => item.script_name)).size;
      const avgVolume =
        historicalData.reduce((sum, item) => sum + (item.volume || 0), 0) /
        historicalData.length;

      setStats({
        totalBreakouts: breakoutCount,
        totalScripts,
        avgVolume: Math.round(avgVolume),
      });
    }
  }, [historicalData]);

  const handleFetchData = async () => {
    if (!date?.from) return;

    setIsLoading(true);
    try {
      // Fetch all data for the date range (simplified - fetches current date data)
      const response = await getData(1, 1000);
      setHistoricalData(response.data);
    } catch (error) {
      console.error('Error fetching historical data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = () => {
    if (historicalData.length > 0) {
      const dateStr = date?.from ? format(date.from, 'yyyy-MM-dd') : 'all';
      exportToCSV(historicalData, `breakout_report_${dateStr}.csv`);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Reports</h1>
        <p className="text-muted-foreground">View historical breakout analysis data</p>
      </div>

      {/* Date Range Picker */}
      <Card>
        <CardHeader>
          <CardTitle>Date Range Selection</CardTitle>
          <CardDescription>Select a date range to view historical data</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  id="date"
                  variant="outline"
                  className={cn(
                    'w-full sm:w-[300px] justify-start text-left font-normal',
                    !date && 'text-muted-foreground'
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {date?.from ? (
                    date.to ? (
                      <>
                        {format(date.from, 'LLL dd, y')} - {format(date.to, 'LLL dd, y')}
                      </>
                    ) : (
                      format(date.from, 'LLL dd, y')
                    )
                  ) : (
                    <span>Pick a date range</span>
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="range"
                  defaultMonth={date?.from}
                  selected={date}
                  onSelect={setDate}
                  numberOfMonths={2}
                />
              </PopoverContent>
            </Popover>

            <div className="flex gap-2">
              <Button onClick={handleFetchData} disabled={!date?.from || isLoading}>
                {isLoading ? 'Loading...' : 'Fetch Data'}
              </Button>
              <Button
                onClick={() =>
                  setDate({
                    from: new Date(),
                    to: new Date(),
                  })
                }
                variant="outline"
              >
                Reset
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Statistics Cards */}
      {historicalData.length > 0 && (
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Breakouts</CardTitle>
              <Badge variant="success">Success</Badge>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalBreakouts}</div>
              <p className="text-xs text-muted-foreground">
                Stocks with breakout indicator
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Scripts</CardTitle>
              <Badge variant="default">Info</Badge>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalScripts}</div>
              <p className="text-xs text-muted-foreground">Unique scripts analyzed</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Volume</CardTitle>
              <Badge variant="warning">Volume</Badge>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.avgVolume.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">Average trading volume</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Historical Data Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Historical Data</CardTitle>
              <CardDescription>
                {historicalData.length > 0
                  ? `Showing ${historicalData.length} records`
                  : 'No data available. Select a date range and click Fetch Data.'}
              </CardDescription>
            </div>
            {historicalData.length > 0 && (
              <Button onClick={handleExport} variant="outline" size="sm">
                <Download className="mr-2 h-4 w-4" />
                Export CSV
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {historicalData.length > 0 ? (
            <div className="relative w-full overflow-auto">
              <table className="w-full caption-bottom text-sm">
                <thead className="[&_tr]:border-b">
                  <tr className="border-b transition-colors hover:bg-muted/50">
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                      Script
                    </th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                      Date
                    </th>
                    <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">
                      Close
                    </th>
                    <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">
                      Volume
                    </th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                      Breakout
                    </th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                      Candle
                    </th>
                  </tr>
                </thead>
                <tbody className="[&_tr:last-child]:border-0">
                  {historicalData.slice(0, 50).map((row, index) => (
                    <tr
                      key={index}
                      className="border-b transition-colors hover:bg-muted/50"
                    >
                      <td className="p-4 align-middle font-medium">{row.script_name}</td>
                      <td className="p-4 align-middle">{row.date}</td>
                      <td className="p-4 align-middle text-right">{row.close?.toFixed(2)}</td>
                      <td className="p-4 align-middle text-right">
                        {row.volume?.toLocaleString()}
                      </td>
                      <td className="p-4 align-middle">
                        <Badge
                          variant={
                            row.breakout_indicator === 'BREAKOUT'
                              ? 'success'
                              : row.breakout_indicator === 'NO_BREAKOUT'
                              ? 'default'
                              : row.breakout_indicator === 'RED_CANDLE'
                              ? 'danger'
                              : 'warning'
                          }
                        >
                          {row.breakout_indicator}
                        </Badge>
                      </td>
                      <td className="p-4 align-middle">
                        <Badge
                          variant={
                            row.candle_indicator === 'GREEN_CANDLE' ? 'success' : 'danger'
                          }
                        >
                          {row.candle_indicator}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {historicalData.length > 50 && (
                <p className="mt-4 text-sm text-muted-foreground text-center">
                  Showing first 50 of {historicalData.length} records. Export CSV to see all
                  data.
                </p>
              )}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">
              Select a date range and click Fetch Data to view historical records
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
