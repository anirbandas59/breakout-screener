import { describe, it, expect } from 'vitest'

// Test utility functions that would be used in the DataTable component
describe('Formatting Utilities', () => {
  describe('formatCurrency', () => {
    const formatCurrency = (value: number) => {
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2,
      }).format(value)
    }

    it('should format currency correctly', () => {
      expect(formatCurrency(2500.50)).toBe('₹2,500.50')
      expect(formatCurrency(1000)).toBe('₹1,000.00')
      expect(formatCurrency(50)).toBe('₹50.00')
    })

    it('should handle large numbers', () => {
      expect(formatCurrency(1500000)).toBe('₹15,00,000.00')
      expect(formatCurrency(10000000)).toBe('₹1,00,00,000.00')
    })

    it('should handle decimal precision', () => {
      expect(formatCurrency(123.456)).toBe('₹123.46')
      expect(formatCurrency(0.99)).toBe('₹0.99')
    })
  })

  describe('formatVolume', () => {
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

    it('should format volume in crores', () => {
      expect(formatVolume(50000000)).toBe('5.0Cr')
      expect(formatVolume(15000000)).toBe('1.5Cr')
      expect(formatVolume(10000000)).toBe('1.0Cr')
    })

    it('should format volume in lakhs', () => {
      expect(formatVolume(5000000)).toBe('50.0L')
      expect(formatVolume(1500000)).toBe('15.0L')
      expect(formatVolume(100000)).toBe('1.0L')
    })

    it('should format volume in thousands', () => {
      expect(formatVolume(50000)).toBe('50.0K')
      expect(formatVolume(15000)).toBe('15.0K')
      expect(formatVolume(1000)).toBe('1.0K')
    })

    it('should format small volumes without suffix', () => {
      expect(formatVolume(999)).toBe('999')
      expect(formatVolume(500)).toBe('500')
      expect(formatVolume(1)).toBe('1')
    })

    it('should handle edge cases', () => {
      expect(formatVolume(0)).toBe('0')
      expect(formatVolume(999999)).toBe('10.0L') // 999999 / 100000 = 9.99999, rounds to 10.0L
      expect(formatVolume(9999999)).toBe('100.0L') // 9999999 / 100000 = 99.99999, rounds to 100.0L
    })
  })

  describe('formatDate', () => {
    it('should format date correctly for Indian locale', () => {
      const date = new Date('2024-01-15')
      const formatted = date.toLocaleDateString('en-IN')
      expect(formatted).toBe('15/1/2024')
    })

    it('should handle different date formats', () => {
      const date1 = new Date('2024-12-31')
      const date2 = new Date('2024-01-01')
      
      expect(date1.toLocaleDateString('en-IN')).toBe('31/12/2024')
      expect(date2.toLocaleDateString('en-IN')).toBe('1/1/2024')
    })
  })

  describe('formatBreakoutStrength', () => {
    const formatBreakoutStrength = (value: number | null | undefined) => {
      if (value === null || value === undefined) return '--'
      return `${value.toFixed(1)}%`
    }

    it('should format positive strength correctly', () => {
      expect(formatBreakoutStrength(15.234)).toBe('15.2%')
      expect(formatBreakoutStrength(5.0)).toBe('5.0%')
    })

    it('should format negative strength correctly', () => {
      expect(formatBreakoutStrength(-8.567)).toBe('-8.6%')
      expect(formatBreakoutStrength(-0.1)).toBe('-0.1%')
    })

    it('should handle null and undefined values', () => {
      expect(formatBreakoutStrength(null)).toBe('--')
      expect(formatBreakoutStrength(undefined)).toBe('--')
    })

    it('should handle zero', () => {
      expect(formatBreakoutStrength(0)).toBe('0.0%')
    })
  })
})