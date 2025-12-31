'use client';

import React, { useEffect } from 'react';
import { useAtom } from 'jotai';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  flexRender,
  createColumnHelper,
  SortingState,
  ColumnDef,
} from '@tanstack/react-table';
import { ArrowUpDown, ArrowUp, ArrowDown, Download } from 'lucide-react';
import Loader from '@/components/Loader/Loader';
import Pagination from '@/components/Pagination/Pagination';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
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
  const [sorting, setSorting] = React.useState<SortingState>([]);

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
      }, 10000); // Reduced from 30s to 10s for better sync with progress

      return () => clearInterval(interval);
    }
  }, [page, limit, startRefresh, refreshTrigger]); // Add refreshTrigger to trigger immediate refresh on task completion

  const columnHelper = createColumnHelper<DataRow>();

  const columns: ColumnDef<DataRow, any>[] = [
    columnHelper.accessor('group_name', {
      header: ({ column }) => {
        return (
          <button
            className="flex items-center gap-1 hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Group
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3" />
            )}
          </button>
        );
      },
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
      header: ({ column }) => {
        return (
          <button
            className="flex items-center gap-1 hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Scripts
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3" />
            )}
          </button>
        );
      },
      cell: (info) => <span className="text-xs font-medium">{info.getValue()}</span>,
    }),
    columnHelper.accessor('breakout_indicator', {
      header: ({ column }) => {
        return (
          <button
            className="flex items-center gap-1 hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Breakout
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3" />
            )}
          </button>
        );
      },
      cell: (info) => (
        <Badge variant={getIndicatorVariant(info.getValue(), 'breakout')} className="text-xs">
          {info.getValue()}
        </Badge>
      ),
    }),
    columnHelper.accessor('candle_indicator', {
      header: ({ column }) => {
        return (
          <button
            className="flex items-center gap-1 hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Candle
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3" />
            )}
          </button>
        );
      },
      cell: (info) => (
        <Badge variant={getIndicatorVariant(info.getValue(), 'candle')} className="text-xs">
          {info.getValue()}
        </Badge>
      ),
    }),
    columnHelper.accessor('volume_indicator', {
      header: ({ column }) => {
        return (
          <button
            className="flex items-center gap-1 hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Volume Indicator
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3" />
            )}
          </button>
        );
      },
      cell: (info) => (
        <Badge variant={getIndicatorVariant(info.getValue(), 'volume')} className="text-xs">
          {info.getValue()}
        </Badge>
      ),
    }),
    columnHelper.accessor('open', {
      header: ({ column }) => {
        return (
          <button
            className="flex items-center gap-1 hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Open
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3" />
            )}
          </button>
        );
      },
      cell: (info) => <span className="text-xs">{info.getValue()}</span>,
    }),
    columnHelper.accessor('high', {
      header: ({ column }) => {
        return (
          <button
            className="flex items-center gap-1 hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            High
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3" />
            )}
          </button>
        );
      },
      cell: (info) => <span className="text-xs">{info.getValue()}</span>,
    }),
    columnHelper.accessor('low', {
      header: ({ column }) => {
        return (
          <button
            className="flex items-center gap-1 hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Low
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3" />
            )}
          </button>
        );
      },
      cell: (info) => <span className="text-xs">{info.getValue()}</span>,
    }),
    columnHelper.accessor('close', {
      header: ({ column }) => {
        return (
          <button
            className="flex items-center gap-1 hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Close
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3" />
            )}
          </button>
        );
      },
      cell: (info) => <span className="text-xs">{info.getValue()}</span>,
    }),
    columnHelper.accessor('previous_high', {
      header: ({ column }) => {
        return (
          <button
            className="flex items-center gap-1 hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            PDH
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3" />
            )}
          </button>
        );
      },
      cell: (info) => <span className="text-xs">{info.getValue()}</span>,
    }),
    columnHelper.accessor('volume', {
      header: ({ column }) => {
        return (
          <button
            className="flex items-center gap-1 hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Volume
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3" />
            )}
          </button>
        );
      },
      cell: (info) => <span className="text-xs">{info.getValue()}</span>,
    }),
    columnHelper.accessor('cpr', {
      header: ({ column }) => {
        return (
          <button
            className="flex items-center gap-1 hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            CPR
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3" />
            )}
          </button>
        );
      },
      cell: (info) => <span className="text-xs">{info.getValue()}</span>,
    }),
    columnHelper.accessor('res1', {
      header: ({ column }) => {
        return (
          <button
            className="flex items-center gap-1 hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            RES-1
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3" />
            )}
          </button>
        );
      },
      cell: (info) => <span className="text-xs">{info.getValue()}</span>,
    }),
    columnHelper.accessor('res2', {
      header: ({ column }) => {
        return (
          <button
            className="flex items-center gap-1 hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            RES-2
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3" />
            )}
          </button>
        );
      },
      cell: (info) => <span className="text-xs">{info.getValue()}</span>,
    }),
    columnHelper.accessor('supp1', {
      header: ({ column }) => {
        return (
          <button
            className="flex items-center gap-1 hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            SUPP-1
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3" />
            )}
          </button>
        );
      },
      cell: (info) => <span className="text-xs">{info.getValue()}</span>,
    }),
    columnHelper.accessor('supp2', {
      header: ({ column }) => {
        return (
          <button
            className="flex items-center gap-1 hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            SUPP-2
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3" />
            )}
          </button>
        );
      },
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
      sorting,
    },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
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
              {table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
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
