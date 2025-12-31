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
import { Download, Search } from 'lucide-react';
import Loader from '@/components/Loader/Loader';
import Pagination from '@/components/Pagination/Pagination';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
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
  const [breakoutFilter, setBreakoutFilter] = useState<string>('all');

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

    if (breakoutFilter && breakoutFilter !== 'all') {
      filters.push({
        id: 'breakout_indicator',
        value: breakoutFilter,
      });
    }

    setColumnFilters(filters);
  }, [searchValue, breakoutFilter]);

  const columnHelper = createColumnHelper<DataRow>();

  const columns: ColumnDef<DataRow, any>[] = [
    columnHelper.accessor('group_name', {
      header: 'Group',
      cell: (info) => <span className="text-xs">{info.getValue()}</span>,
    }),
    columnHelper.display({
      id: 'sl_no',
      header: 'Sl. No',
      cell: ({ row }) => (
        <span className="text-xs">{row.index + 1 + (page - 1) * limit}</span>
      ),
    }),
    columnHelper.accessor('script_name', {
      header: 'Scripts',
      cell: (info) => <span className="text-xs font-medium">{info.getValue()}</span>,
      filterFn: 'includesString',
    }),
    columnHelper.accessor('breakout_indicator', {
      header: 'Breakout',
      cell: (info) => (
        <Badge variant={getIndicatorVariant(info.getValue(), 'breakout')} className="text-xs">
          {info.getValue()}
        </Badge>
      ),
      filterFn: (row, id, value) => {
        return row.getValue(id) === value;
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
    const date = new Date().toISOString().split('T')[0];
    exportToCSV(data, `breakout_data_${date}.csv`);
  };

  // Get unique breakout indicator values for filter dropdown
  const breakoutValues = React.useMemo(() => {
    const unique = new Set(data.map((row) => row.breakout_indicator).filter(Boolean));
    return Array.from(unique).sort();
  }, [data]);

  return (
    <>
      <div className="flex justify-between items-center mb-4">
        <Pagination
          currentPage={page}
          totalPages={totalRecords}
          limit={limit}
          onPageChange={handlePageChange}
          onLimitChange={handleLimitChange}
        />
        {data.length > 0 && (
          <Button
            onClick={handleExport}
            variant="outline"
            size="sm"
            className="gap-2"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </Button>
        )}
      </div>

      {/* Filters Section */}
      {data.length > 0 && (
        <div className="flex gap-4 mb-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by symbol name..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              className="pl-8"
            />
          </div>
          <Select value={breakoutFilter} onValueChange={setBreakoutFilter}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Filter by Breakout" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Breakouts</SelectItem>
              {breakoutValues.map((value) => (
                <SelectItem key={value} value={value}>
                  {value}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

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
