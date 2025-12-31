'use client';

import React, { useEffect, useState } from 'react';
import { useAtom } from 'jotai';
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  flexRender,
  createColumnHelper,
  ColumnDef,
  ColumnFiltersState,
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
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([]);
  const [searchValue, setSearchValue] = useState('');
  const [selectedBreakouts, setSelectedBreakouts] = useState<string[]>([]);

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

    if (startRefresh) {
      const interval = setInterval(() => {
        fetchData(page, limit);
      }, 10000);

      return () => clearInterval(interval);
    }
  }, [page, limit, startRefresh, refreshTrigger]);

  // Update column filters when search or breakout filter changes
  useEffect(() => {
    const filters: ColumnFiltersState = [];

    if (searchValue) {
      filters.push({
        id: 'script_name',
        value: searchValue,
      });
    }

    if (selectedBreakouts.length > 0) {
      filters.push({
        id: 'breakout_indicator',
        value: selectedBreakouts,
      });
    }

    setColumnFilters(filters);
  }, [searchValue, selectedBreakouts]);

  const columnHelper = createColumnHelper<DataRow>();

  // Get unique breakout indicator values for filter
  const breakoutValues = React.useMemo(() => {
    const unique = new Set(data.map((row) => row.breakout_indicator).filter(Boolean));
    return Array.from(unique).sort();
  }, [data]);

  const handleBreakoutToggle = (value: string) => {
    setSelectedBreakouts((prev) =>
      prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]
    );
  };

  const columns: ColumnDef<DataRow, any>[] = [
    columnHelper.accessor('script_name', {
      header: 'Scripts',
      cell: (info) => <span className="text-xs font-medium">{info.getValue()}</span>,
      filterFn: 'includesString',
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
      filterFn: (row, id, value: string[]) => {
        if (!value || value.length === 0) return true;
        return value.includes(row.getValue(id));
      },
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
    state: {
      columnFilters,
    },
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handleLimitChange = (newLimit: number) => {
    setLimit(newLimit);
    setPage(1);
  };

  const handleExport = () => {
    const exportDate = date || new Date().toISOString().split('T')[0];
    exportToCSV(data, `breakout_data_${exportDate}.csv`);
  };

  return (
    <>
      <div className="space-y-4 mb-4">
        {/* Line 1: Date and Pagination */}
        <div className="flex items-center justify-between gap-4">
          <div className="text-sm font-medium">
            Date: <span className="text-muted-foreground">{date || 'Not set'}</span>
          </div>
          <Pagination
            currentPage={page}
            totalPages={totalRecords}
            limit={limit}
            onPageChange={handlePageChange}
            onLimitChange={handleLimitChange}
          />
        </div>

        {/* Line 2: Search and Export */}
        {data.length > 0 && (
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
        ) : data.length > 0 ? (
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
                    <span className="text-sm text-muted-foreground">No results found</span>
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
