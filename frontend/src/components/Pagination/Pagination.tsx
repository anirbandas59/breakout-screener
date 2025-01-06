import React, { ChangeEvent } from 'react';
import ArrowBackIosRoundedIcon from '@mui/icons-material/ArrowBackIosRounded';
import ArrowForwardIosRoundedIcon from '@mui/icons-material/ArrowForwardIosRounded';
import SyncRoundedIcon from '@mui/icons-material/SyncRounded';

interface PaginationProps {
  date: string;
  currentPage: number;
  totalPages: number;
  limit: number;
  onPageChange: (newPage: number) => void;
  onLimitChange: (newLimit: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({
  date,
  currentPage,
  totalPages,
  limit,
  onPageChange,
  onLimitChange,
}) => {
  const handlePrevious = (): void => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = (): void => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1);
    }
  };

  const handleLimitChange = (e: ChangeEvent<HTMLSelectElement>): void => {
    const newLimit = parseInt(e.target.value);
    onLimitChange(newLimit);
  };

  return (
    <div className="flex items-center justify-between p-4">
      <div className="flex items-center gap-2">
        <span className="icon-[mdi-light--home] text-xs hover:bg-blue-200 p-1 rounded-full">
          <SyncRoundedIcon className="dark:text-white dark:hover:text-black" />
        </span>
        <span className="dark:text-white text-sm sm:text-xs">
          Date <strong>{date}</strong>
        </span>
      </div>

      {/* Page Navigation */}
      {totalPages > 0 ? (
        <div className="flex gap-4 items-center">
          <button
            className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 dark:bg-gray-600 disabled:opacity-50"
            onClick={handlePrevious}
            disabled={currentPage === 1}
          >
            <ArrowBackIosRoundedIcon className="w-8 h-8" />
          </button>
          <span className="dark:text-white text-sm sm:text-xs">
            Page <strong>{currentPage}</strong> of <strong>{Math.ceil(totalPages / limit)}</strong>
          </span>
          <button
            className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 dark:bg-gray-600 disabled:opacity-50"
            onClick={handleNext}
            disabled={currentPage === totalPages}
          >
            <ArrowForwardIosRoundedIcon className="w-8 h-8" />
          </button>
        </div>
      ) : (
        <span>&nbsp;</span>
      )}

      {/* Limit Selection */}
      {totalPages > 0 ? (
        <div className="flex items-center gap-2">
          <label htmlFor="limit" className="text-sm sm:text-xs">
            Rows per page:
          </label>
          <select
            id="limit"
            value={limit}
            onChange={handleLimitChange}
            className="px-2 py-1 border rounded sm:text-xs text-sm dark:text-gray-500"
          >
            {[10, 20, 30, 50].map((value) => (
              <option key={value} value={value} className="sm:text-xs text-sm dark:text-gray-500">
                {value}
              </option>
            ))}
          </select>
        </div>
      ) : (
        <span>&nbsp;</span>
      )}
    </div>
  );
};

export default Pagination;
