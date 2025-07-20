'use client'

import Link from 'next/link'
import { useTheme } from 'next-themes'
import { Button } from '@/components/ui/button'
import { Moon, Sun, BarChart3 } from 'lucide-react'

export default function Header() {
  const { theme, setTheme } = useTheme()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo and Brand */}
        <div className="flex items-center space-x-4">
          <Link href="/" className="flex items-center space-x-2">
            <BarChart3 className="h-8 w-8 text-primary" />
            <span className="font-bold text-xl tracking-tight">
              Breakout Screener V2
            </span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="hidden md:flex items-center space-x-6">
          <Link 
            href="/screener" 
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Stock Screener
          </Link>
          <Link 
            href="/analysis" 
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Analysis
          </Link>
          <Link 
            href="/settings" 
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Settings
          </Link>
        </nav>

        {/* Theme Toggle */}
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="h-9 w-9"
          >
            <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">Toggle theme</span>
          </Button>
        </div>
      </div>
    </header>
  )
}