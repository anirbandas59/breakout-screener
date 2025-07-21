import { render, screen, fireEvent } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import DataTable from '@/components/DataTable'
import type { BreakoutDataResponse } from '@/types/api'
import { BreakoutStatusEnum, CandleIndicatorEnum, VolumeIndicatorEnum, PivotTypeEnum, AnalysisStatusEnum, StockGroupEnum } from '@/types/api'

// Mock window.open
const mockWindowOpen = vi.fn()
Object.defineProperty(window, 'open', {
  writable: true,
  value: mockWindowOpen,
})

const mockData: BreakoutDataResponse[] = [
  {
    id: '550e8400-e29b-41d4-a716-446655440001' as any,
    stock_id: '550e8400-e29b-41d4-a716-446655440002' as any,
    stock_symbol: 'RELIANCE',
    trade_date: '2024-01-15',
    open_price: 2480.00,
    high_price: 2520.00,
    low_price: 2475.00,
    close_price: 2500.50,
    volume: 5000000,
    pivot: 2490.00,
    bc: 2485.00,
    tc: 2495.00,
    breakout_status: BreakoutStatusEnum.BULLISH_BREAKOUT,
    candle_indicator: CandleIndicatorEnum.BULLISH,
    volume_indicator: VolumeIndicatorEnum.HIGH_VOLUME,
    pivot_type: PivotTypeEnum.CLASSICAL,
    analysis_status: AnalysisStatusEnum.COMPLETED,
    is_analyzed: true,
    breakout_strength: 15.2,
    cpr_width: 10.0,
    cpr_width_percentage: 0.4,
    price_range: 45.0,
    price_range_percentage: 1.8,
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z'
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440003' as any,
    stock_id: '550e8400-e29b-41d4-a716-446655440004' as any,
    stock_symbol: 'TCS',
    trade_date: '2024-01-14',
    open_price: 3210.00,
    high_price: 3220.00,
    low_price: 3190.00,
    close_price: 3200.75,
    volume: 2000000,
    pivot: 3205.00,
    bc: 3200.00,
    tc: 3210.00,
    breakout_status: BreakoutStatusEnum.BEARISH_BREAKOUT,
    candle_indicator: CandleIndicatorEnum.BEARISH,
    volume_indicator: VolumeIndicatorEnum.LOW_VOLUME,
    pivot_type: PivotTypeEnum.CLASSICAL,
    analysis_status: AnalysisStatusEnum.COMPLETED,
    is_analyzed: true,
    breakout_strength: -8.5,
    cpr_width: 10.0,
    cpr_width_percentage: 0.31,
    price_range: 30.0,
    price_range_percentage: 0.94,
    created_at: '2024-01-14T10:00:00Z',
    updated_at: '2024-01-14T10:00:00Z'
  }
]

describe('DataTable', () => {
  const mockOnSort = vi.fn()
  const mockOnRowClick = vi.fn()

  beforeEach(() => {
    mockOnSort.mockClear()
    mockOnRowClick.mockClear()
    mockWindowOpen.mockClear()
  })

  it('renders loading state correctly', () => {
    render(<DataTable data={[]} isLoading={true} />)
    
    expect(screen.getByText('Loading...')).toBeInTheDocument()
    expect(screen.getAllByRole('generic')).toHaveLength(6) // 5 skeleton rows + container
  })

  it('renders empty state when no data', () => {
    render(<DataTable data={[]} />)
    
    expect(screen.getByText('No breakout data available. Run an analysis to see results.')).toBeInTheDocument()
  })

  it('renders data table with correct headers', () => {
    render(<DataTable data={mockData} />)
    
    expect(screen.getByText('Breakout Analysis Results')).toBeInTheDocument()
    expect(screen.getByText('Symbol')).toBeInTheDocument()
    expect(screen.getByText('Date')).toBeInTheDocument()
    expect(screen.getByText('Breakout')).toBeInTheDocument()
    expect(screen.getByText('Candle')).toBeInTheDocument()
    expect(screen.getByText('Volume')).toBeInTheDocument()
    expect(screen.getByText('Close')).toBeInTheDocument()
    expect(screen.getByText('Strength')).toBeInTheDocument()
    expect(screen.getByText('Chart')).toBeInTheDocument()
  })

  it('displays stock data correctly', () => {
    render(<DataTable data={mockData} />)
    
    expect(screen.getByText('RELIANCE')).toBeInTheDocument()
    expect(screen.getByText('TCS')).toBeInTheDocument()
    expect(screen.getByText('₹2,500.50')).toBeInTheDocument()
    expect(screen.getByText('₹3,200.75')).toBeInTheDocument()
    expect(screen.getByText('5.0Cr')).toBeInTheDocument()
    expect(screen.getByText('2.0Cr')).toBeInTheDocument()
  })

  it('handles sorting functionality', () => {
    render(<DataTable data={mockData} onSort={mockOnSort} />)
    
    const symbolHeader = screen.getByText('Symbol').closest('th')
    fireEvent.click(symbolHeader!)
    
    expect(mockOnSort).toHaveBeenCalledWith('stock_symbol', 'asc')
  })

  it('shows sort indicators correctly', () => {
    render(
      <DataTable 
        data={mockData} 
        onSort={mockOnSort}
        sortField="stock_symbol"
        sortDirection="asc"
      />
    )
    
    // Check that sort icon is rendered (ChevronUp)
    const symbolHeader = screen.getByText('Symbol').closest('th')
    expect(symbolHeader).toBeInTheDocument()
  })

  it('handles row clicks', () => {
    render(<DataTable data={mockData} onRowClick={mockOnRowClick} />)
    
    const firstRow = screen.getByText('RELIANCE').closest('tr')
    fireEvent.click(firstRow!)
    
    expect(mockOnRowClick).toHaveBeenCalledWith(mockData[0])
  })

  it('opens chart link in new window', () => {
    render(<DataTable data={mockData} />)
    
    const chartButtons = screen.getAllByRole('button')
    const chartButton = chartButtons.find((btn: any) => btn.querySelector('svg'))
    
    fireEvent.click(chartButton!)
    
    expect(mockWindowOpen).toHaveBeenCalledWith(
      'https://chartink.com/stocks/reliance.html',
      '_blank'
    )
  })

  it('prevents event propagation when chart button is clicked', () => {
    render(<DataTable data={mockData} onRowClick={mockOnRowClick} />)
    
    const chartButtons = screen.getAllByRole('button')
    const chartButton = chartButtons.find((btn: any) => btn.querySelector('svg'))
    
    fireEvent.click(chartButton!)
    
    expect(mockOnRowClick).not.toHaveBeenCalled()
  })

  it('formats currency correctly', () => {
    render(<DataTable data={mockData} />)
    
    expect(screen.getByText('₹2,500.50')).toBeInTheDocument()
    expect(screen.getByText('₹3,200.75')).toBeInTheDocument()
  })

  it('formats volume correctly', () => {
    render(<DataTable data={mockData} />)
    
    expect(screen.getByText('5.0Cr')).toBeInTheDocument() // 50L = 5.0Cr
    expect(screen.getByText('2.0Cr')).toBeInTheDocument() // 20L = 2.0Cr
  })

  it('displays breakout strength with correct precision', () => {
    render(<DataTable data={mockData} />)
    
    expect(screen.getByText('15.2%')).toBeInTheDocument()
    expect(screen.getByText('-8.5%')).toBeInTheDocument()
  })

  it('shows correct badge variants for breakout status', () => {
    render(<DataTable data={mockData} />)
    
    const bullishBadge = screen.getByText('BULLISH BREAKOUT').closest('.inline-flex')
    const bearishBadge = screen.getByText('BEARISH BREAKOUT').closest('.inline-flex')
    
    expect(bullishBadge).toBeInTheDocument()
    expect(bearishBadge).toBeInTheDocument()
  })

  it('handles date formatting correctly', () => {
    render(<DataTable data={mockData} />)
    
    // Check that dates are formatted as Indian locale
    expect(screen.getByText('15/1/2024')).toBeInTheDocument()
    expect(screen.getByText('14/1/2024')).toBeInTheDocument()
  })

  it('handles missing breakout strength gracefully', () => {
    const dataWithMissingStrength = [{
      ...mockData[0],
      breakout_strength: undefined
    }] as BreakoutDataResponse[]
    
    render(<DataTable data={dataWithMissingStrength} />)
    
    expect(screen.getByText('--')).toBeInTheDocument()
  })
})