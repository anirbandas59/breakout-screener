/**
 * React Query hooks for stock API endpoints
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import type {
  StockResponse,
  StockList,
  StockFilter,
  BreakoutDataList,
  BreakoutDataFilter,
} from '@/types/api'

// Query keys
export const stockKeys = {
  all: ['stocks'] as const,
  lists: () => [...stockKeys.all, 'list'] as const,
  list: (filters: StockFilter) => [...stockKeys.lists(), filters] as const,
  details: () => [...stockKeys.all, 'detail'] as const,
  detail: (id: string) => [...stockKeys.details(), id] as const,
  search: (query: string) => [...stockKeys.all, 'search', query] as const,
  breakoutData: (stockId: string, filters?: BreakoutDataFilter) => 
    [...stockKeys.detail(stockId), 'breakout-data', filters] as const,
}

// Hooks for stocks
export function useStocks(filters: StockFilter = {}) {
  return useQuery({
    queryKey: stockKeys.list(filters),
    queryFn: () => apiClient.get<StockList>('/stocks/', filters),
    placeholderData: (previousData) => previousData,
  })
}

export function useStock(id: string) {
  return useQuery({
    queryKey: stockKeys.detail(id),
    queryFn: () => apiClient.get<StockResponse>(`/stocks/${id}`),
    enabled: !!id,
  })
}

export function useStockSearch(query: string) {
  return useQuery({
    queryKey: stockKeys.search(query),
    queryFn: () => apiClient.get<StockList>('/stocks/search', { query, limit: 10 }),
    enabled: query.length >= 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export function useStockBreakoutData(stockId: string, filters: BreakoutDataFilter = {}) {
  return useQuery({
    queryKey: stockKeys.breakoutData(stockId, filters),
    queryFn: () => apiClient.get<BreakoutDataList>(`/stocks/${stockId}/breakout-data`, filters),
    enabled: !!stockId,
    placeholderData: (previousData) => previousData,
  })
}

// Mutations
export function useCreateStock() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: any) => apiClient.post<StockResponse>('/stocks/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: stockKeys.lists() })
    },
  })
}

export function useUpdateStock() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      apiClient.put<StockResponse>(`/stocks/${id}`, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: stockKeys.detail(variables.id) })
      queryClient.invalidateQueries({ queryKey: stockKeys.lists() })
    },
  })
}

export function useDeleteStock() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/stocks/${id}`),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: stockKeys.detail(id) })
      queryClient.invalidateQueries({ queryKey: stockKeys.lists() })
    },
  })
}