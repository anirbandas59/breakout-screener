/**
 * React Query hooks for analysis API endpoints
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import type {
  AnalysisSessionResponse,
  AnalysisSessionList,
  AnalysisSessionFilter,
  BulkAnalysisRequest,
  BulkAnalysisResult,
  TaskResponse,
} from '@/types/api'

// Query keys
export const analysisKeys = {
  all: ['analysis'] as const,
  sessions: () => [...analysisKeys.all, 'sessions'] as const,
  sessionsList: (filters: AnalysisSessionFilter) =>
    [...analysisKeys.sessions(), 'list', filters] as const,
  session: (id: string) => [...analysisKeys.sessions(), id] as const,
  tasks: () => [...analysisKeys.all, 'tasks'] as const,
  task: (id: string) => [...analysisKeys.tasks(), id] as const,
  metrics: () => [...analysisKeys.all, 'metrics'] as const,
}

// Analysis Sessions
export function useAnalysisSessions(filters: AnalysisSessionFilter = {}) {
  return useQuery({
    queryKey: analysisKeys.sessionsList(filters),
    queryFn: () =>
      apiClient.get<AnalysisSessionList>('/analysis/sessions/', filters),
    placeholderData: (previousData) => previousData,
  })
}

export function useAnalysisSession(id: string) {
  return useQuery({
    queryKey: analysisKeys.session(id),
    queryFn: () =>
      apiClient.get<AnalysisSessionResponse>(`/analysis/sessions/${id}`),
    enabled: !!id,
  })
}

// Task Status Polling
export function useTaskStatus(taskId: string, enabled = true) {
  return useQuery({
    queryKey: analysisKeys.task(taskId),
    queryFn: () =>
      apiClient.get<TaskResponse>(`/analysis/tasks/${taskId}/status`),
    enabled: !!taskId && enabled,
    refetchInterval: (query) => {
      // Continue polling if task is still running
      const data = query?.state?.data
      if (data?.status === 'PENDING' || data?.status === 'IN_PROGRESS') {
        return 5000 // Poll every 5 seconds
      }
      return false // Stop polling when done
    },
    retry: (failureCount, error: any) => {
      // Don't retry if task not found
      if (error?.response?.status === 404) {
        return false
      }
      return failureCount < 3
    },
  })
}

// Generate breakout data
export function useGenerateBreakoutData() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: { date: string; pivot_val: number }) =>
      apiClient.post<TaskResponse>('/analysis/generate-breakout-data', data),
    onSuccess: (data) => {
      // Start polling for task status
      queryClient.setQueryData(analysisKeys.task(data.task_id), data)
    },
  })
}

// Bulk analysis
export function useBulkAnalysis() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: BulkAnalysisRequest) =>
      apiClient.post<BulkAnalysisResult>('/analysis/bulk-analyze', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: analysisKeys.sessions() })
    },
  })
}

// Fetch scripts
export function useFetchScripts() {
  return useMutation({
    mutationFn: () => apiClient.post<TaskResponse>('/analysis/fetch-scripts'),
  })
}

// Clear data operations
export function useClearChartData() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () =>
      apiClient.post<TaskResponse>('/analysis/clear-chart-data'),
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: ['breakout-data'] })
    },
  })
}

export function useClearCompleteData() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () =>
      apiClient.post<TaskResponse>('/analysis/clear-complete-data'),
    onSuccess: () => {
      // Invalidate all data queries
      queryClient.invalidateQueries({ queryKey: ['stocks'] })
      queryClient.invalidateQueries({ queryKey: ['breakout-data'] })
      queryClient.invalidateQueries({ queryKey: analysisKeys.sessions() })
    },
  })
}

// Suspend analysis
export function useSuspendAnalysis() {
  return useMutation({
    mutationFn: () => apiClient.post('/analysis/suspend'),
  })
}

// Create analysis session
export function useCreateAnalysisSession() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: any) =>
      apiClient.post<AnalysisSessionResponse>('/analysis/sessions/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: analysisKeys.sessions() })
    },
  })
}

// Update analysis session
export function useUpdateAnalysisSession() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      apiClient.put<AnalysisSessionResponse>(`/analysis/sessions/${id}`, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({
        queryKey: analysisKeys.session(variables.id),
      })
      queryClient.invalidateQueries({ queryKey: analysisKeys.sessions() })
    },
  })
}
