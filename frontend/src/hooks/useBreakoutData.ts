'use client';

import { useEffect, useState } from 'react';
import { useAtom } from 'jotai';
import { useDebounce } from 'use-debounce';
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
import { DataRow } from '@/types/AppInterfaces';
import { getData } from '@/services/api';
import { exportToCSV } from '@/utils/csvExport';

export interface BreakoutDataState {
  // Data
  data: DataRow[];
  dataDate: string | null;
  dataSource: string | null;
  // Pagination
  page: number;
  limit: number;
  totalRecords: number;
  // Search & Filters
  searchValue: string;
  selectedBreakouts: string[];
  // UI state
  isLoading: boolean;
  hasFiltersOrSearch: boolean;
  shouldShowTable: boolean;
  // Handlers
  setSearchValue: (v: string) => void;
  handleBreakoutToggle: (value: string) => void;
  handlePageChange: (newPage: number) => void;
  handleLimitChange: (newLimit: number) => void;
  handleClearFilters: () => void;
  handleExport: () => void;
  formatDisplayDate: (dateStr: string | null) => string;
}

/**
 * Custom hook that encapsulates all data fetching, filtering, pagination,
 * and state management for the breakout data table.
 *
 * Extracted from DataTable.tsx to separate data concerns from presentation.
 */
export function useBreakoutData(): BreakoutDataState {
  const [date] = useAtom(dateAtom);
  const [page, setPage] = useAtom(tablePageAtom);
  const [limit, setLimit] = useAtom(tableLimitAtom);
  const [totalRecords, setTotalRecords] = useAtom(totalRecordsAtom);
  const [isLoading, setIsLoading] = useAtom(isLoadingAtom);
  const [startRefresh] = useAtom(startRefreshAtom);
  const [refreshTrigger] = useAtom(refreshTriggerAtom);
  const [, setScriptsAnalyzed] = useAtom(scriptsAnalyzedAtom);

  const [data, setData] = useState<DataRow[]>([]);
  const [searchValue, setSearchValue] = useState('');
  const [selectedBreakouts, setSelectedBreakouts] = useState<string[]>([]);
  const [dataDate, setDataDate] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<string | null>(null);

  const [debouncedSearch] = useDebounce(searchValue, 300);

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
      console.error('Error fetching data', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Main data fetching effect
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
    if (page !== 1) setPage(1);
  }, [debouncedSearch]);

  // Reset to page 1 when breakout filters change
  useEffect(() => {
    if (page !== 1 && selectedBreakouts.length > 0) setPage(1);
  }, [selectedBreakouts]);

  const handleBreakoutToggle = (value: string) => {
    setSelectedBreakouts((prev) =>
      prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]
    );
  };

  const handlePageChange = (newPage: number) => setPage(newPage);

  const handleLimitChange = (newLimit: number) => {
    setLimit(newLimit);
    setPage(1);
  };

  const handleClearFilters = () => setSelectedBreakouts([]);

  const handleExport = () => {
    const exportDate = dataDate || date || new Date().toISOString().split('T')[0];
    exportToCSV(data, `breakout_data_${exportDate}.csv`);
  };

  const formatDisplayDate = (dateStr: string | null): string => {
    if (!dateStr) return 'Not available';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const hasFiltersOrSearch = searchValue !== '' || selectedBreakouts.length > 0;
  const shouldShowTable = data.length > 0 || hasFiltersOrSearch;

  return {
    data,
    dataDate,
    dataSource,
    page,
    limit,
    totalRecords,
    searchValue,
    selectedBreakouts,
    isLoading,
    hasFiltersOrSearch,
    shouldShowTable,
    setSearchValue,
    handleBreakoutToggle,
    handlePageChange,
    handleLimitChange,
    handleClearFilters,
    handleExport,
    formatDisplayDate,
  };
}
