'use client'

import React, { useState, useEffect } from 'react'
import { format } from 'date-fns'

import InputForm from '@/components/InputForm'
import ButtonGroups from '@/components/ButtonGroups'
import DataTable from '@/components/DataTable'
import Header from '@/components/Header'

import { useBreakoutDataRealtime } from '@/hooks/api/breakout-data'
import {
  useGenerateBreakoutData,
  useFetchScripts,
  useClearChartData,
  useClearCompleteData,
  useSuspendAnalysis,
  useTaskStatus,
} from '@/hooks/api/analysis'

import type { BreakoutDataFilter } from '@/types/api'

interface AnalysisFormData {
  analysisDate: string
  pivotGap: number
  startFrom?: number
}

export default function HomePage() {
  // State management
  const [analysisDate, setAnalysisDate] = useState(() => 
    format(new Date(), 'yyyy-MM-dd')
  )
  const [currentTaskId, setCurrentTaskId] = useState<string>('')
  const [isAnalysisRunning, setIsAnalysisRunning] = useState(false)
  const [scriptsAnalyzed, setScriptsAnalyzed] = useState(0)
  const [startTime, setStartTime] = useState<string>('')
  const [runningTime, setRunningTime] = useState<string>('')
  const [scriptFetchedOn, setScriptFetchedOn] = useState<string>('')

  // Data table state
  const [sortField, setSortField] = useState<string>()
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc')

  // Filters for data table
  const [dataFilters, setDataFilters] = useState<BreakoutDataFilter>({
    trade_date_from: analysisDate,
    trade_date_to: analysisDate,
    page: 1,
    limit: 50,
    sort_by: sortField,
    sort_order: sortDirection,
  })

  // API hooks
  const { data: breakoutData, isLoading: isLoadingData } = useBreakoutDataRealtime(
    dataFilters,
    isAnalysisRunning
  )

  const generateBreakoutMutation = useGenerateBreakoutData()
  const fetchScriptsMutation = useFetchScripts()
  const clearChartMutation = useClearChartData()
  const clearCompleteMutation = useClearCompleteData()
  const suspendMutation = useSuspendAnalysis()

  // Task status polling
  const { data: taskStatus } = useTaskStatus(currentTaskId, !!currentTaskId)

  // Update analysis state based on task status
  useEffect(() => {
    if (taskStatus) {
      const { status, result } = taskStatus

      setIsAnalysisRunning(
        status === 'PENDING' || status === 'IN_PROGRESS'
      )

      if (result?.start_time) {
        setStartTime(result.start_time)
      }

      if (status === 'COMPLETED' && result?.end_time) {
        setScriptFetchedOn(result.end_time)
        setRunningTime(calculateDuration(result.start_time, result.end_time))
        setIsAnalysisRunning(false)
        setCurrentTaskId('')
      } else if (status === 'FAILED') {
        setIsAnalysisRunning(false)
        setCurrentTaskId('')
      }

      // Update scripts analyzed count (if available in result)
      if (result && 'processed_items' in result) {
        setScriptsAnalyzed(result.processed_items || 0)
      }
    }
  }, [taskStatus])

  // Update running time every second when analysis is running
  useEffect(() => {
    if (!isAnalysisRunning || !startTime) return

    const interval = setInterval(() => {
      const now = new Date().toISOString()
      setRunningTime(calculateDuration(startTime, now))
    }, 1000)

    return () => clearInterval(interval)
  }, [isAnalysisRunning, startTime])

  // Update data filters when date or sorting changes
  useEffect(() => {
    setDataFilters(prev => ({
      ...prev,
      trade_date_from: analysisDate,
      trade_date_to: analysisDate,
      sort_by: sortField,
      sort_order: sortDirection,
    }))
  }, [analysisDate, sortField, sortDirection])

  // Helper function to calculate duration
  const calculateDuration = (start: string, end: string): string => {
    try {
      const startDate = new Date(start)
      const endDate = new Date(end)
      const diffMs = endDate.getTime() - startDate.getTime()
      
      const hours = Math.floor(diffMs / (1000 * 60 * 60))
      const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((diffMs % (1000 * 60)) / 1000)
      
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    } catch {
      return '--:--:--'
    }
  }

  // Format timestamp for display
  const formatDateTime = (timestamp: string): string => {
    if (!timestamp) return '--'
    try {
      return format(new Date(timestamp), 'dd/MM/yyyy HH:mm:ss')
    } catch {
      return '--'
    }
  }

  // Event handlers
  const handleAnalysisSubmit = (data: AnalysisFormData) => {
    setAnalysisDate(data.analysisDate)
    
    generateBreakoutMutation.mutate({
      date: data.analysisDate,
      pivot_val: data.pivotGap / 100, // Convert percentage to decimal
    }, {
      onSuccess: (response) => {
        setCurrentTaskId(response.task_id)
        setIsAnalysisRunning(true)
        setStartTime(new Date().toISOString())
        setScriptsAnalyzed(0)
        setRunningTime('00:00:00')
      },
      onError: (error) => {
        console.error('Failed to start analysis:', error)
        setIsAnalysisRunning(false)
      }
    })
  }

  const handleDateChange = (date: string) => {
    setAnalysisDate(date)
  }

  const handleStopAnalysis = () => {
    suspendMutation.mutate(undefined, {
      onSuccess: () => {
        setIsAnalysisRunning(false)
        setCurrentTaskId('')
      }
    })
  }

  const handleFetchScripts = () => {
    fetchScriptsMutation.mutate(undefined, {
      onSuccess: (response) => {
        setCurrentTaskId(response.task_id)
      }
    })
  }

  const handleClearChart = () => {
    clearChartMutation.mutate(undefined, {
      onSuccess: (response) => {
        setCurrentTaskId(response.task_id)
      }
    })
  }

  const handleClearComplete = () => {
    clearCompleteMutation.mutate(undefined, {
      onSuccess: (response) => {
        setCurrentTaskId(response.task_id)
        setScriptsAnalyzed(0)
        setStartTime('')
        setRunningTime('')
        setScriptFetchedOn('')
      }
    })
  }

  const handleSort = (field: string, direction: 'asc' | 'desc') => {
    setSortField(field)
    setSortDirection(direction)
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto px-4 py-6 space-y-6">
        {/* Analysis Configuration */}
        <InputForm
          analysisDate={analysisDate}
          startTime={formatDateTime(startTime)}
          runningTime={runningTime}
          scriptFetchedOn={formatDateTime(scriptFetchedOn)}
          scriptsAnalyzed={scriptsAnalyzed}
          onSubmit={handleAnalysisSubmit}
          onDateChange={handleDateChange}
          isAnalysisRunning={isAnalysisRunning}
        />

        {/* Action Buttons */}
        <ButtonGroups
          onStart={() => {}} // Handled by form submit
          onStop={handleStopAnalysis}
          onClear={handleClearChart}
          onFetchList={handleFetchScripts}
          onClearList={handleClearComplete}
          isAnalysisRunning={isAnalysisRunning}
          isLoading={{
            stop: suspendMutation.isPending,
            clear: clearChartMutation.isPending,
            fetchList: fetchScriptsMutation.isPending,
            clearList: clearCompleteMutation.isPending,
          }}
        />

        {/* Data Table */}
        <DataTable
          data={breakoutData?.items || []}
          isLoading={isLoadingData}
          onSort={handleSort}
          sortField={sortField}
          sortDirection={sortDirection}
          onRowClick={(item) => {
            console.log('Row clicked:', item)
            // Could open a detail view or chart
          }}
        />
      </main>
    </div>
  )
}