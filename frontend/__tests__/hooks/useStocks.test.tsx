import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi } from 'vitest'
import { useStocks, useStock, useStockSearch, stockKeys } from '@/hooks/api/stocks'
import { apiClient } from '@/lib/api-client'
import type { StockList, StockResponse } from '@/types/api'

// Mock api client
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockedApiClient = vi.mocked(apiClient)

// Test wrapper with QueryClient
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

const mockStockList: StockList = {
  items: [
    {
      id: 1,
      symbol: 'RELIANCE',
      company_name: 'Reliance Industries Limited',
      sector: 'Energy',
      market_cap: 1500000000000,
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    }
  ],
  total: 1,
  page: 1,
  size: 20,
  pages: 1
}

const mockStock: StockResponse = {
  id: 1,
  symbol: 'RELIANCE',
  company_name: 'Reliance Industries Limited',
  sector: 'Energy',
  market_cap: 1500000000000,
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
}

describe('Stock Hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('useStocks', () => {
    it('should fetch stocks list successfully', async () => {
      mockedApiClient.get.mockResolvedValue(mockStockList)

      const { result } = renderHook(() => useStocks(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(mockedApiClient.get).toHaveBeenCalledWith('/stocks/', {})
      expect(result.current.data).toEqual(mockStockList)
    })

    it('should pass filters to API call', async () => {
      const filters = { sector: 'Energy', page: 1, size: 10 }
      mockedApiClient.get.mockResolvedValue(mockStockList)

      renderHook(() => useStocks(filters), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(mockedApiClient.get).toHaveBeenCalledWith('/stocks/', filters)
      })
    })

    it('should handle API errors', async () => {
      const error = new Error('Network error')
      mockedApiClient.get.mockRejectedValue(error)

      const { result } = renderHook(() => useStocks(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })

      expect(result.current.error).toEqual(error)
    })

    it('should use correct query key', () => {
      const filters = { sector: 'Energy' }
      const queryKey = stockKeys.list(filters)
      
      expect(queryKey).toEqual(['stocks', 'list', filters])
    })
  })

  describe('useStock', () => {
    it('should fetch single stock successfully', async () => {
      mockedApiClient.get.mockResolvedValue(mockStock)

      const { result } = renderHook(() => useStock('1'), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(mockedApiClient.get).toHaveBeenCalledWith('/stocks/1')
      expect(result.current.data).toEqual(mockStock)
    })

    it('should not fetch when id is empty', () => {
      renderHook(() => useStock(''), {
        wrapper: createWrapper(),
      })

      expect(mockedApiClient.get).not.toHaveBeenCalled()
    })

    it('should use correct query key', () => {
      const queryKey = stockKeys.detail('1')
      
      expect(queryKey).toEqual(['stocks', 'detail', '1'])
    })
  })

  describe('useStockSearch', () => {
    it('should search stocks successfully', async () => {
      const searchQuery = 'RELI'
      mockedApiClient.get.mockResolvedValue(mockStockList)

      const { result } = renderHook(() => useStockSearch(searchQuery), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(mockedApiClient.get).toHaveBeenCalledWith('/stocks/search', {
        query: searchQuery,
        limit: 10
      })
      expect(result.current.data).toEqual(mockStockList)
    })

    it('should not search when query is less than 2 characters', () => {
      renderHook(() => useStockSearch('R'), {
        wrapper: createWrapper(),
      })

      expect(mockedApiClient.get).not.toHaveBeenCalled()
    })

    it('should use correct query key', () => {
      const query = 'RELI'
      const queryKey = stockKeys.search(query)
      
      expect(queryKey).toEqual(['stocks', 'search', query])
    })

    it('should have correct stale time', async () => {
      mockedApiClient.get.mockResolvedValue(mockStockList)

      const { result } = renderHook(() => useStockSearch('RELI'), {
        wrapper: createWrapper(),
      })

      // Wait for initial fetch
      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      // Should not refetch immediately due to staleTime
      vi.clearAllMocks()
      
      // Re-render with same query
      renderHook(() => useStockSearch('RELI'), {
        wrapper: createWrapper(),
      })

      // Should not make another API call due to staleTime
      expect(mockedApiClient.get).not.toHaveBeenCalled()
    })
  })

  describe('stockKeys', () => {
    it('should generate correct key structure', () => {
      expect(stockKeys.all).toEqual(['stocks'])
      expect(stockKeys.lists()).toEqual(['stocks', 'list'])
      expect(stockKeys.details()).toEqual(['stocks', 'detail'])
      
      const filters = { sector: 'Energy' }
      expect(stockKeys.list(filters)).toEqual(['stocks', 'list', filters])
      expect(stockKeys.detail('1')).toEqual(['stocks', 'detail', '1'])
      expect(stockKeys.search('RELI')).toEqual(['stocks', 'search', 'RELI'])
    })

    it('should generate breakout data keys correctly', () => {
      const filters = { limit: 10 }
      const key = stockKeys.breakoutData('1', filters)
      
      expect(key).toEqual(['stocks', 'detail', '1', 'breakout-data', filters])
    })
  })
})