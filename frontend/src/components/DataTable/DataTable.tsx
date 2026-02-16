'use client';

import React from 'react';
import { useReactTable, getCoreRowModel, flexRender } from '@tanstack/react-table';
import { Download, Search } from 'lucide-react';
import Loader from '@/components/Loader/Loader';
import Pagination from '@/components/Pagination/Pagination';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useBreakoutData } from '@/hooks/useBreakoutData';
import { useDataTableColumns } from './DataTableColumns';

const DataTable: React.FC = () => {
  const {
    data,
    dataDate,
    dataSource,
    page,
    limit,
    totalRecords,
    searchValue,
    selectedBreakouts,
    isLoading,
    shouldShowTable,
    setSearchValue,
    handleBreakoutToggle,
    handlePageChange,
    handleLimitChange,
    handleClearFilters,
    handleExport,
    formatDisplayDate,
  } = useBreakoutData();

  const columns = useDataTableColumns({
    selectedBreakouts,
    onBreakoutToggle: handleBreakoutToggle,
    onClearFilters: handleClearFilters,
  });

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

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

        {/* Line 2: Search and Export */}
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
