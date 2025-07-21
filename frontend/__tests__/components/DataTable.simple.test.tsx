import { describe, it, expect } from 'vitest'
import { BreakoutStatusEnum, CandleIndicatorEnum, VolumeIndicatorEnum } from '@/types/api'

// Test utility functions and enums
describe('DataTable Utilities', () => {
  it('should validate enum values', () => {
    expect(BreakoutStatusEnum.BULLISH_BREAKOUT).toBe('BULLISH_BREAKOUT')
    expect(BreakoutStatusEnum.BEARISH_BREAKOUT).toBe('BEARISH_BREAKOUT')
    expect(CandleIndicatorEnum.BULLISH).toBe('BULLISH')
    expect(VolumeIndicatorEnum.HIGH_VOLUME).toBe('HIGH_VOLUME')
  })

  it('should format breakout status for display', () => {
    const formatBreakoutStatus = (status: string) => status.replace('_', ' ')
    
    expect(formatBreakoutStatus('BULLISH_BREAKOUT')).toBe('BULLISH BREAKOUT')
    expect(formatBreakoutStatus('BEARISH_BREAKOUT')).toBe('BEARISH BREAKOUT')
  })

  it('should get correct badge variants', () => {
    function getBreakoutStatusVariant(status: string): 'default' | 'secondary' | 'destructive' | 'outline' {
      switch (status) {
        case 'BULLISH_BREAKOUT':
          return 'default'
        case 'BEARISH_BREAKOUT':
          return 'destructive'
        default:
          return 'secondary'
      }
    }

    expect(getBreakoutStatusVariant('BULLISH_BREAKOUT')).toBe('default')
    expect(getBreakoutStatusVariant('BEARISH_BREAKOUT')).toBe('destructive')
    expect(getBreakoutStatusVariant('NO_BREAKOUT')).toBe('secondary')
  })
})