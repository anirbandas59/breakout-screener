/**
 * React Query hooks for breakout data API endpoints
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import type {
  BreakoutDataResponse,
  BreakoutDataList,
  BreakoutDataFilter,
} from '@/types/api'

// Query keys
export const breakoutDataKeys = {
  all: ['breakout-data'] as const,
  lists: () => [...breakoutDataKeys.all, 'list'] as const,
  list: (filters: BreakoutDataFilter) => [...breakoutDataKeys.lists(), filters] as const,
  details: () => [...breakoutDataKeys.all, 'detail'] as const,
  detail: (id: string) => [...breakoutDataKeys.details(), id] as const,
  summary: (filters?: BreakoutDataFilter) => [...breakoutDataKeys.all, 'summary', filters] as const,
  daily: (date: string) => [...breakoutDataKeys.all, 'daily', date] as const,
}

// Get breakout data with filtering and pagination
export function useBreakoutData(filters: BreakoutDataFilter = {}) {
  return useQuery({
    queryKey: breakoutDataKeys.list(filters),
    queryFn: () => apiClient.get<BreakoutDataList>('/breakout-data/', filters),
    placeholderData: (previousData) => previousData,
    staleTime: 30 * 1000, // 30 seconds - data changes frequently during analysis
  })
}

// Get single breakout data record
export function useBreakoutDataDetail(id: string) {
  return useQuery({
    queryKey: breakoutDataKeys.detail(id),
    queryFn: () => apiClient.get<BreakoutDataResponse>(`/breakout-data/${id}`),
    enabled: !!id,
  })
}

// Get breakout data summary
export function useBreakoutDataSummary(filters: BreakoutDataFilter = {}) {
  return useQuery({
    queryKey: breakoutDataKeys.summary(filters),
    queryFn: () => apiClient.get('/breakout-data/summary', filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

// Get daily breakout summary
export function useDailyBreakoutSummary(date: string) {
  return useQuery({
    queryKey: breakoutDataKeys.daily(date),
    queryFn: () => apiClient.get(`/breakout-data/daily-summary`, { date }),
    enabled: !!date,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Auto-refreshing query for real-time data during analysis
export function useBreakoutDataRealtime(filters: BreakoutDataFilter = {}, enabled = false) {
  return useQuery({
    queryKey: [...breakoutDataKeys.list(filters), 'realtime'],
    queryFn: () => apiClient.get<BreakoutDataList>('/breakout-data/', filters),
    enabled,
    refetchInterval: enabled ? 10000 : false, // Refresh every 10 seconds when enabled
    placeholderData: (previousData) => previousData,
  })
}

// Mutations
export function useCreateBreakoutData() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: any) =>
      apiClient.post<BreakoutDataResponse>('/breakout-data/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: breakoutDataKeys.lists() })
      queryClient.invalidateQueries({ queryKey: breakoutDataKeys.summary() })
    },
  })
}

export function useUpdateBreakoutData() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      apiClient.put<BreakoutDataResponse>(`/breakout-data/${id}`, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: breakoutDataKeys.detail(variables.id) })
      queryClient.invalidateQueries({ queryKey: breakoutDataKeys.lists() })
      queryClient.invalidateQueries({ queryKey: breakoutDataKeys.summary() })
    },
  })
}

export function useDeleteBreakoutData() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/breakout-data/${id}`),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: breakoutDataKeys.detail(id) })
      queryClient.invalidateQueries({ queryKey: breakoutDataKeys.lists() })
      queryClient.invalidateQueries({ queryKey: breakoutDataKeys.summary() })
    },
  })
}

// Bulk analyze breakout data
export function useBulkAnalyzeBreakoutData() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: any) =>
      apiClient.post('/breakout-data/bulk-analyze', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: breakoutDataKeys.lists() })
      queryClient.invalidateQueries({ queryKey: breakoutDataKeys.summary() })
    },
  })
}

// Export breakout data
export function useExportBreakoutData() {
  return useMutation({
    mutationFn: (filters: BreakoutDataFilter & { format: string }) =>
      apiClient.post('/breakout-data/export', filters, {
        responseType: 'blob',
      }),
  })
}