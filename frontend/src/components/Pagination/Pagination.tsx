import React, { ChangeEvent } from 'react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  limit: number;
  onPageChange: (newPage: number) => void;
  onLimitChange: (newLimit: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({
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
    <div className="flex items-center gap-4">
      {/* Page Navigation */}
      {totalPages > 0 && (
        <>
          <div className="flex gap-2 items-center">
            <button
              className="px-3 py-1 bg-secondary rounded hover:bg-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={handlePrevious}
              disabled={currentPage <= 1}
            >
              ←
            </button>
            <span className="text-sm">
              Page <strong>{currentPage}</strong> of <strong>{Math.ceil(totalPages / limit)}</strong>
            </span>
            <button
              className="px-3 py-1 bg-secondary rounded hover:bg-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={handleNext}
              disabled={currentPage >= Math.ceil(totalPages / limit)}
            >
              →
            </button>
          </div>

          {/* Limit Selection */}
          <div className="flex items-center gap-2">
            <label htmlFor="limit" className="text-sm">
              Rows per page:
            </label>
            <select
              id="limit"
              value={limit}
              onChange={handleLimitChange}
              className="px-2 py-1 border rounded text-sm bg-background"
            >
              {[10, 20, 30, 50].map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </div>
        </>
      )}
    </div>
  );
};

export default Pagination;
