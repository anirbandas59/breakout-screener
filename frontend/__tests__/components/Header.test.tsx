import { render, screen, fireEvent } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import Header from '@/components/Header'

// Mock next-themes
const mockSetTheme = vi.fn()
vi.mock('next-themes', () => ({
  useTheme: () => ({
    theme: 'light',
    setTheme: mockSetTheme,
  }),
}))

describe('Header', () => {
  beforeEach(() => {
    mockSetTheme.mockClear()
  })

  it('renders the header with logo and brand name', () => {
    render(<Header />)
    
    expect(screen.getByText('Breakout Screener V2')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /breakout screener v2/i })).toHaveAttribute('href', '/')
  })

  it('renders navigation links', () => {
    render(<Header />)
    
    expect(screen.getByRole('link', { name: 'Stock Screener' })).toHaveAttribute('href', '/screener')
    expect(screen.getByRole('link', { name: 'Analysis' })).toHaveAttribute('href', '/analysis')
    expect(screen.getByRole('link', { name: 'Settings' })).toHaveAttribute('href', '/settings')
  })

  it('renders theme toggle button', () => {
    render(<Header />)
    
    const themeToggle = screen.getByRole('button', { name: /toggle theme/i })
    expect(themeToggle).toBeInTheDocument()
  })

  it('calls setTheme when theme toggle is clicked', () => {
    render(<Header />)
    
    const themeToggle = screen.getByRole('button', { name: /toggle theme/i })
    fireEvent.click(themeToggle)
    
    expect(mockSetTheme).toHaveBeenCalledWith('dark')
  })

  it('switches theme from dark to light when clicked', () => {
    vi.mocked(vi.importMock('next-themes')).useTheme.mockReturnValue({
      theme: 'dark',
      setTheme: mockSetTheme,
    })
    
    render(<Header />)
    
    const themeToggle = screen.getByRole('button', { name: /toggle theme/i })
    fireEvent.click(themeToggle)
    
    expect(mockSetTheme).toHaveBeenCalledWith('light')
  })

  it('has proper styling classes', () => {
    render(<Header />)
    
    const header = screen.getByRole('banner')
    expect(header).toHaveClass('sticky', 'top-0', 'z-50', 'w-full', 'border-b')
  })

  it('has responsive navigation that hides on mobile', () => {
    render(<Header />)
    
    const nav = screen.getByRole('navigation')
    expect(nav).toHaveClass('hidden', 'md:flex')
  })
})