'use client';

import React, { useEffect, useState } from 'react';
import { useAtom } from 'jotai';
import { useDebounce } from 'use-debounce';
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  createColumnHelper,
  ColumnDef,
} from '@tanstack/react-table';
import { Download, Search, Filter } from 'lucide-react';
import Loader from '@/components/Loader/Loader';
import Pagination from '@/components/Pagination/Pagination';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { DataRow } from '@/types/AppInterfaces';
import { getData } from '@/services/api';
import { exportToCSV } from '@/utils/csvExport';
import {
  dateAtom,
  tablePageAtom,
  tableLimitAtom,
  totalRecordsAtom,
  isLoadingAtom,
  startRefreshAtom,
  refreshTriggerAtom,
  scriptsAnalyzedAtom,
} from '@/store/atoms';

// Helper function to get indicator badge variant
const getIndicatorVariant = (
  value: string | null | undefined,
  type: 'breakout' | 'candle' | 'volume'
): 'success' | 'warning' | 'danger' | 'default' => {
  if (!value) return 'default';

  const normalized = value.toLowerCase().trim();

  if (type === 'breakout') {
    if (normalized === 'breakout') return 'success';
    if (normalized === 'red candle') return 'warning';
    if (normalized === 'no breakout') return 'default';
    if (normalized === 'big sell wick') return 'danger';
    if (normalized === 'no entry') return 'default';
  } else if (type === 'candle') {
    if (normalized === 'green candle') return 'success';
    if (normalized === 'red candle') return 'danger';
    if (normalized === 'doji') return 'warning';
  } else if (type === 'volume') {
    if (normalized === 'good') return 'success';
    if (normalized === 'average') return 'warning';
    if (normalized === 'low') return 'danger';
  }

  return 'default';
};

const DataTable: React.FC = () => {
  const [date] = useAtom(dateAtom);
  const [page, setPage] = useAtom(tablePageAtom);
  const [limit, setLimit] = useAtom(tableLimitAtom);
  const [totalRecords, setTotalRecords] = useAtom(totalRecordsAtom);
  const [isLoading, setIsLoading] = useAtom(isLoadingAtom);
  const [startRefresh] = useAtom(startRefreshAtom);
  const [refreshTrigger] = useAtom(refreshTriggerAtom);
  const [, setScriptsAnalyzed] = useAtom(scriptsAnalyzedAtom);

  const [data, setData] = React.useState<DataRow[]>([]);
  const [searchValue, setSearchValue] = useState('');
  const [selectedBreakouts, setSelectedBreakouts] = useState<string[]>([]);
  const [dataDate, setDataDate] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<string | null>(null);

  // Debounce search value to avoid excessive API calls
  const [debouncedSearch] = useDebounce(searchValue, 300);

  // Hardcoded breakout indicator values (must match database values exactly)
  const breakoutValues = ['Breakout', 'Red candle', 'no breakout', 'Big Sell Wick'];

  const fetchData = async (
    page: number,
    limit: number,
    search?: string,
    breakoutFilters?: string[]
  ) => {
    setIsLoading(true);

    try {
      const response = await getData(page, limit, search, breakoutFilters);
      const { total, data, data_date, data_source } = response;

      setData(data);
      setTotalRecords(total);
      setScriptsAnalyzed(total);
      setDataDate(data_date || null);
      setDataSource(data_source || null);
    } catch (error) {
      console.error('Error fetching error', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Main data fetching effect - triggers on page, limit, or refreshTrigger changes
  useEffect(() => {
    fetchData(page, limit, debouncedSearch, selectedBreakouts);

    if (startRefresh) {
      const interval = setInterval(() => {
        fetchData(page, limit, debouncedSearch, selectedBreakouts);
      }, 10000);

      return () => clearInterval(interval);
    }
  }, [page, limit, startRefresh, refreshTrigger, debouncedSearch, selectedBreakouts]);

  // Reset to page 1 when search changes
  useEffect(() => {
    if (page !== 1) {
      setPage(1);
    }
  }, [debouncedSearch]);

  // Reset to page 1 when breakout filters change
  useEffect(() => {
    if (page !== 1 && selectedBreakouts.length > 0) {
      setPage(1);
    }
  }, [selectedBreakouts]);

  const columnHelper = createColumnHelper<DataRow>();

  const handleBreakoutToggle = (value: string) => {
    setSelectedBreakouts((prev) =>
      prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]
    );
  };

  const columns: ColumnDef<DataRow, any>[] = [
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
                {breakoutValues.map((value) => (
                  <div key={value} className="flex items-center space-x-2">
                    <Checkbox
                      id={`breakout-${value}`}
                      checked={selectedBreakouts.includes(value)}
                      onCheckedChange={() => handleBreakoutToggle(value)}
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
                    onClick={() => setSelectedBreakouts([])}
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
  ];

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handleLimitChange = (newLimit: number) => {
    setLimit(newLimit);
    setPage(1);
  };

  const handleExport = () => {
    const exportDate = dataDate || date || new Date().toISOString().split('T')[0];
    exportToCSV(data, `breakout_data_${exportDate}.csv`);
  };

  // Format date for display (YYYY-MM-DD to DD-MMM-YYYY)
  const formatDisplayDate = (dateStr: string | null): string => {
    if (!dateStr) return 'Not available';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  // Check if any filters or search are active
  const hasFiltersOrSearch = searchValue !== '' || selectedBreakouts.length > 0;

  // Determine if we should show the table:
  // - Show table when data exists OR when filters/search are active (so user can clear them)
  const shouldShowTable = data.length > 0 || hasFiltersOrSearch;

  return (
    <>
      <div className="space-y-4 mb-4">
        {/* Line 1: Date and Pagination */}
        <div className="flex items-center justify-between gap-4">
          <div className="text-sm font-medium">
            Data Date:{' '}
            <span className="text-muted-foreground">
              {formatDisplayDate(dataDate)}
            </span>
            {dataSource === 'master_breakout_data' && (
              <span className="ml-2 text-xs text-amber-600 dark:text-amber-400">(Historical)</span>
            )}
          </div>
          <Pagination
            currentPage={page}
            totalPages={totalRecords}
            limit={limit}
            onPageChange={handlePageChange}
            onLimitChange={handleLimitChange}
          />
        </div>

        {/* Line 2: Search and Export - show when data exists or filters are active */}
        {shouldShowTable && (
          <div className="flex items-center justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by symbol..."
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                className="pl-8"
                size={undefined}
              />
            </div>
            <Button
              onClick={handleExport}
              variant="outline"
              size="sm"
              className="gap-2"
              disabled={data.length === 0}
            >
              <Download className="h-4 w-4" />
              Export CSV
            </Button>
          </div>
        )}
      </div>

      <div className="rounded-lg border shadow-md">
        {isLoading ? (
          <Loader />
        ) : shouldShowTable ? (
          <Table>
            <TableHeader>
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <TableHead key={header.id} className="text-xs font-semibold">
                      {header.isPlaceholder
                        ? null
                        : flexRender(header.column.columnDef.header, header.getContext())}
                    </TableHead>
                  ))}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {table.getRowModel().rows.length > 0 ? (
                table.getRowModel().rows.map((row) => (
                  <TableRow key={row.id}>
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={columns.length} className="text-center py-4">
                    <span className="text-sm text-muted-foreground">
                      No results found for the selected filters
                    </span>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        ) : (
          <div className="flex justify-center p-4 border rounded-lg">
            <span className="text-sm text-muted-foreground">No data to display</span>
          </div>
        )}
      </div>
    </>
  );
};

export default DataTable;
