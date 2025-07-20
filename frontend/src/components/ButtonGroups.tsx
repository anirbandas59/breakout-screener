'use client'

import React from 'react'
import { Button } from '@/components/ui/button'
import { 
  Play, 
  Square, 
  Trash2, 
  Download, 
  RefreshCw,
  Loader2
} from 'lucide-react'

interface ButtonGroupsProps {
  onStart: () => void
  onStop: () => void
  onClear: () => void
  onFetchList: () => void
  onClearList: () => void
  isAnalysisRunning?: boolean
  isLoading?: {
    start?: boolean
    stop?: boolean
    clear?: boolean
    fetchList?: boolean
    clearList?: boolean
  }
  disabled?: boolean
}

export default function ButtonGroups({
  onStart,
  onStop,
  onClear,
  onFetchList,
  onClearList,
  isAnalysisRunning = false,
  isLoading = {},
  disabled = false,
}: ButtonGroupsProps) {
  return (
    <div className="flex flex-col space-y-4">
      {/* Primary Actions */}
      <div className="flex flex-wrap gap-3">
        <Button
          onClick={onStart}
          disabled={disabled || isAnalysisRunning || isLoading.start}
          className="min-w-[120px]"
          size="default"
        >
          {isLoading.start ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Starting...
            </>
          ) : (
            <>
              <Play className="mr-2 h-4 w-4" />
              Start Analysis
            </>
          )}
        </Button>

        <Button
          onClick={onStop}
          disabled={disabled || !isAnalysisRunning || isLoading.stop}
          variant="destructive"
          className="min-w-[120px]"
          size="default"
        >
          {isLoading.stop ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Stopping...
            </>
          ) : (
            <>
              <Square className="mr-2 h-4 w-4" />
              Stop Analysis
            </>
          )}
        </Button>
      </div>

      {/* Secondary Actions */}
      <div className="flex flex-wrap gap-3">
        <Button
          onClick={onFetchList}
          disabled={disabled || isAnalysisRunning || isLoading.fetchList}
          variant="outline"
          className="min-w-[120px]"
          size="default"
        >
          {isLoading.fetchList ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Fetching...
            </>
          ) : (
            <>
              <Download className="mr-2 h-4 w-4" />
              Fetch Scripts
            </>
          )}
        </Button>

        <Button
          onClick={onClear}
          disabled={disabled || isAnalysisRunning || isLoading.clear}
          variant="outline"
          className="min-w-[120px]"
          size="default"
        >
          {isLoading.clear ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Clearing...
            </>
          ) : (
            <>
              <RefreshCw className="mr-2 h-4 w-4" />
              Clear Chart
            </>
          )}
        </Button>

        <Button
          onClick={onClearList}
          disabled={disabled || isAnalysisRunning || isLoading.clearList}
          variant="outline"
          className="min-w-[120px]"
          size="default"
        >
          {isLoading.clearList ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Clearing...
            </>
          ) : (
            <>
              <Trash2 className="mr-2 h-4 w-4" />
              Clear All Data
            </>
          )}
        </Button>
      </div>

      {/* Status Indicator */}
      {isAnalysisRunning && (
        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Analysis is currently running...</span>
        </div>
      )}
    </div>
  )
}