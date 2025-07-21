import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Breakout Screener V2',
  description: 'Advanced breakout stock screener with real-time data analysis',
  keywords: [
    'stock screener',
    'breakout analysis',
    'NSE data',
    'financial analysis',
  ],
  authors: [{ name: 'Breakout Screener Team' }],
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
