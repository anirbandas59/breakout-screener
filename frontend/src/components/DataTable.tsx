'use client'

import React, { useState } from 'react'
import { 
  ChevronUpIcon, 
  ChevronDownIcon, 
  ExternalLinkIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  MinusIcon
} from 'lucide-react'

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

import type { BreakoutDataResponse, BreakoutDataFilter } from '@/types/api'

interface DataTableProps {
  data: BreakoutDataResponse[]
  isLoading?: boolean
  onSort?: (field: string, direction: 'asc' | 'desc') => void
  sortField?: string
  sortDirection?: 'asc' | 'desc'
  onRowClick?: (item: BreakoutDataResponse) => void
}

type SortableField = keyof Pick<BreakoutDataResponse, 
  | 'stock_symbol' 
  | 'trade_date'
  | 'close_price'
  | 'volume'
  | 'breakout_status'
  | 'candle_indicator'
  | 'volume_indicator'
  | 'breakout_strength'
>

const COLUMN_HEADERS: Array<{
  key: SortableField | 'actions'
  label: string
  sortable: boolean
  className?: string
}> = [
  { key: 'stock_symbol', label: 'Symbol', sortable: true },
  { key: 'trade_date', label: 'Date', sortable: true },
  { key: 'breakout_status', label: 'Breakout', sortable: true },
  { key: 'candle_indicator', label: 'Candle', sortable: true },
  { key: 'volume_indicator', label: 'Volume', sortable: true },
  { key: 'close_price', label: 'Close', sortable: true, className: 'text-right' },
  { key: 'volume', label: 'Volume', sortable: true, className: 'text-right' },
  { key: 'breakout_strength', label: 'Strength', sortable: true, className: 'text-center' },
  { key: 'actions', label: 'Chart', sortable: false, className: 'text-center' },
]

function getBreakoutStatusIcon(status: string) {
  switch (status) {
    case 'BULLISH_BREAKOUT':
      return <TrendingUpIcon className="h-3 w-3" />
    case 'BEARISH_BREAKOUT':
      return <TrendingDownIcon className="h-3 w-3" />
    default:
      return <MinusIcon className="h-3 w-3" />
  }
}

function getBreakoutStatusVariant(status: string): "default" | "secondary" | "destructive" | "outline" {
  switch (status) {
    case 'BULLISH_BREAKOUT':
      return 'default'
    case 'BEARISH_BREAKOUT':
      return 'destructive'
    default:
      return 'secondary'
  }
}

function getCandleIndicatorVariant(indicator: string): "default" | "secondary" | "destructive" | "outline" {
  switch (indicator) {
    case 'BULLISH':
    case 'HAMMER':
      return 'default'
    case 'BEARISH':
    case 'SHOOTING_STAR':
      return 'destructive'
    default:
      return 'secondary'
  }
}

function getVolumeIndicatorVariant(indicator: string): "default" | "secondary" | "destructive" | "outline" {
  switch (indicator) {
    case 'HIGH_VOLUME':
    case 'UNUSUAL_VOLUME':
      return 'default'
    case 'LOW_VOLUME':
      return 'destructive'
    default:
      return 'secondary'
  }
}

export default function DataTable({
  data,
  isLoading = false,
  onSort,
  sortField,
  sortDirection,
  onRowClick,
}: DataTableProps) {
  const handleSort = (field: SortableField) => {
    if (!onSort) return
    
    const newDirection = 
      sortField === field && sortDirection === 'asc' ? 'desc' : 'asc'
    onSort(field, newDirection)
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(value)
  }

  const formatVolume = (value: number) => {
    if (value >= 10000000) {
      return `${(value / 10000000).toFixed(1)}Cr`
    } else if (value >= 100000) {
      return `${(value / 100000).toFixed(1)}L`
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K`
    }
    return value.toLocaleString()
  }

  const renderSortIcon = (field: SortableField) => {
    if (sortField !== field) return null
    return sortDirection === 'asc' ? 
      <ChevronUpIcon className="h-4 w-4" /> : 
      <ChevronDownIcon className="h-4 w-4" />
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading...</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-12 bg-muted animate-pulse rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!data || data.length === 0) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="text-center text-muted-foreground">
            No breakout data available. Run an analysis to see results.
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Breakout Analysis Results</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                {COLUMN_HEADERS.map((header) => (
                  <TableHead 
                    key={header.key} 
                    className={`${header.className || ''} ${header.sortable ? 'cursor-pointer select-none hover:bg-muted/50' : ''}`}
                    onClick={() => header.sortable && onSort && handleSort(header.key as SortableField)}
                  >
                    <div className="flex items-center space-x-1">
                      <span>{header.label}</span>
                      {header.sortable && renderSortIcon(header.key as SortableField)}
                    </div>
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((item, index) => (
                <TableRow 
                  key={item.id || index}
                  className={onRowClick ? 'cursor-pointer' : ''}
                  onClick={() => onRowClick?.(item)}
                >
                  <TableCell className="font-medium">
                    {item.stock_symbol || 'N/A'}
                  </TableCell>
                  
                  <TableCell>
                    {new Date(item.trade_date).toLocaleDateString('en-IN')}
                  </TableCell>
                  
                  <TableCell>
                    <Badge 
                      variant={getBreakoutStatusVariant(item.breakout_status)}
                      className="flex items-center space-x-1"
                    >
                      {getBreakoutStatusIcon(item.breakout_status)}
                      <span className="text-xs">
                        {item.breakout_status.replace('_', ' ')}
                      </span>
                    </Badge>
                  </TableCell>
                  
                  <TableCell>
                    <Badge variant={getCandleIndicatorVariant(item.candle_indicator)}>
                      {item.candle_indicator}
                    </Badge>
                  </TableCell>
                  
                  <TableCell>
                    <Badge variant={getVolumeIndicatorVariant(item.volume_indicator)}>
                      {item.volume_indicator.replace('_', ' ')}
                    </Badge>
                  </TableCell>
                  
                  <TableCell className="text-right font-mono">
                    {formatCurrency(item.close_price)}
                  </TableCell>
                  
                  <TableCell className="text-right font-mono">
                    {formatVolume(item.volume)}
                  </TableCell>
                  
                  <TableCell className="text-center">
                    {item.breakout_strength ? (
                      <div className="flex items-center justify-center">
                        <div className="text-sm font-medium">
                          {item.breakout_strength.toFixed(1)}%
                        </div>
                      </div>
                    ) : (
                      <span className="text-muted-foreground">--</span>
                    )}
                  </TableCell>
                  
                  <TableCell className="text-center">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        // Open chart in new window
                        window.open(
                          `https://chartink.com/stocks/${item.stock_symbol?.toLowerCase()}.html`,
                          '_blank'
                        )
                      }}
                    >
                      <ExternalLinkIcon className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}