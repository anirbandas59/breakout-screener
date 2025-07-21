/**
 * TypeScript interfaces for V2 API schemas
 * Based on Pydantic schemas from backend
 */

import { UUID } from 'crypto'

// Base types
export interface BaseResponse {
  id: UUID
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

export interface ListResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  has_next: boolean
  has_previous: boolean
}

export interface FilterParams {
  page?: number
  limit?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

// Enums
export enum StockGroupEnum {
  NIFTY_50 = 'NIFTY_50',
  NIFTY_100 = 'NIFTY_100',
  NIFTY_500 = 'NIFTY_500',
  MIDCAP = 'MIDCAP',
  SMALLCAP = 'SMALLCAP',
}

export enum BreakoutStatusEnum {
  NO_BREAKOUT = 'NO_BREAKOUT',
  BULLISH_BREAKOUT = 'BULLISH_BREAKOUT',
  BEARISH_BREAKOUT = 'BEARISH_BREAKOUT',
  SIDEWAYS = 'SIDEWAYS',
}

export enum CandleIndicatorEnum {
  BULLISH = 'BULLISH',
  BEARISH = 'BEARISH',
  DOJI = 'DOJI',
  HAMMER = 'HAMMER',
  SHOOTING_STAR = 'SHOOTING_STAR',
  NEUTRAL = 'NEUTRAL',
}

export enum VolumeIndicatorEnum {
  HIGH_VOLUME = 'HIGH_VOLUME',
  AVERAGE_VOLUME = 'AVERAGE_VOLUME',
  LOW_VOLUME = 'LOW_VOLUME',
  UNUSUAL_VOLUME = 'UNUSUAL_VOLUME',
}

export enum PivotTypeEnum {
  CLASSICAL = 'CLASSICAL',
  FIBONACCI = 'FIBONACCI',
  CAMARILLA = 'CAMARILLA',
  WOODIE = 'WOODIE',
}

export enum AnalysisStatusEnum {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED',
}

export enum PerformanceMetricTypeEnum {
  ACCURACY = 'ACCURACY',
  PRECISION = 'PRECISION',
  RECALL = 'RECALL',
  F1_SCORE = 'F1_SCORE',
  SUCCESS_RATE = 'SUCCESS_RATE',
}

// Stock schemas
export interface StockBase {
  symbol: string
  company_name: string
  stock_group: StockGroupEnum
  sector?: string
  market_cap?: number
  is_active: boolean
}

export interface StockResponse extends StockBase, BaseResponse {
  breakout_data_count?: number
  latest_breakout_date?: string
}

export interface StockList extends ListResponse<StockResponse> {}

export interface StockFilter extends FilterParams {
  symbol?: string
  company_name?: string
  stock_group?: StockGroupEnum
  sector?: string
  is_active?: boolean
  market_cap_min?: number
  market_cap_max?: number
}

// Breakout Data schemas
export interface BreakoutDataBase {
  stock_id: UUID
  trade_date: string
  open_price: number
  high_price: number
  low_price: number
  close_price: number
  volume: number
  pivot: number
  bc: number
  tc: number
  candle_indicator: CandleIndicatorEnum
  volume_indicator: VolumeIndicatorEnum
  breakout_status: BreakoutStatusEnum
  pivot_type: PivotTypeEnum
  analysis_status: AnalysisStatusEnum
  is_analyzed: boolean
  avg_volume_10d?: number
  volume_ratio?: number
  price_change_pct?: number
  breakout_strength?: number
  is_narrow_gap?: boolean
  gap_percentage?: number
}

export interface BreakoutDataResponse extends BreakoutDataBase, BaseResponse {
  stock_symbol?: string
  stock_company_name?: string
  trading_day_of_week?: string
  is_weekend?: boolean
  cpr_width: number
  cpr_width_percentage: number
  price_range: number
  price_range_percentage: number
}

export interface BreakoutDataList extends ListResponse<BreakoutDataResponse> {}

export interface BreakoutDataFilter extends FilterParams {
  stock_id?: UUID
  symbol?: string
  trade_date_from?: string
  trade_date_to?: string
  breakout_status?: BreakoutStatusEnum
  pivot_type?: PivotTypeEnum
  analysis_status?: AnalysisStatusEnum
  is_analyzed?: boolean
  min_price?: number
  max_price?: number
  min_volume?: number
  max_volume?: number
  min_cpr_width?: number
  max_cpr_width?: number
  candle_indicator?: CandleIndicatorEnum
  volume_indicator?: VolumeIndicatorEnum
  has_breakout?: boolean
  is_narrow_gap?: boolean
  min_breakout_strength?: number
}

// Analysis Session schemas
export interface AnalysisSessionBase {
  session_name: string
  analysis_date: string
  status: AnalysisStatusEnum
  start_time?: string
  end_time?: string
  analysis_parameters?: Record<string, any>
  data_source?: string
  total_items?: number
  processed_items?: number
  success_count?: number
  error_count?: number
  warning_count?: number
  description?: string
  tags?: string[]
}

export interface AnalysisSessionResponse
  extends AnalysisSessionBase,
    BaseResponse {
  is_running: boolean
  is_completed: boolean
  has_errors: boolean
  metrics_count?: number
  success_rate?: number
  progress_percentage?: number
  duration_seconds?: number
  estimated_completion_time?: string
}

export interface AnalysisSessionList
  extends ListResponse<AnalysisSessionResponse> {}

export interface AnalysisSessionFilter extends FilterParams {
  session_name?: string
  status?: AnalysisStatusEnum
  analysis_date_from?: string
  analysis_date_to?: string
  data_source?: string
  min_progress?: number
  max_progress?: number
  min_success_rate?: number
  has_errors?: boolean
  has_metrics?: boolean
  tags?: string[]
  created_by?: string
}

// Performance Metrics schemas
export interface PerformanceMetricsBase {
  session_id: UUID
  metric_type: PerformanceMetricTypeEnum
  metric_date: string
  metric_value: number
  metric_unit?: string
  metric_description?: string
  context_data?: Record<string, any>
  tags?: string[]
}

export interface PerformanceMetricsResponse
  extends PerformanceMetricsBase,
    BaseResponse {
  session_name?: string
  session_status?: string
  is_latest: boolean
  days_ago?: number
}

export interface PerformanceMetricsList
  extends ListResponse<PerformanceMetricsResponse> {}

// API request/response types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  errors?: string[]
}

export interface TaskResponse {
  task_id: string
  status: string
  result?: {
    status: string
    message?: string
    start_time?: string
    end_time?: string
    progress?: number
  }
  error?: string
}

export interface BulkAnalysisRequest {
  trade_date_from: string
  trade_date_to: string
  symbols?: string[]
  force_reanalysis?: boolean
  analysis_params?: Record<string, any>
}

export interface BulkAnalysisResult {
  total_requested: number
  successfully_analyzed: number
  failed_analysis: number
  skipped_existing: number
  analysis_errors: Array<Record<string, any>>
  processing_time_seconds: number
  success_rate: number
}

// Frontend-specific types
export interface AnalysisFormData {
  date: string
  pivot_gap: number
  start_from?: number
}

export interface AppError {
  message: string
  code?: string
  details?: any
}

export interface PaginationInfo {
  page: number
  limit: number
  total: number
  hasNext: boolean
  hasPrevious: boolean
}

// Health check response
export interface HealthResponse {
  status: string
  version: string
  timestamp: string
  components: {
    database: {
      status: string
      response_time_ms?: number
    }
    redis: {
      status: string
      response_time_ms?: number
    }
  }
}
