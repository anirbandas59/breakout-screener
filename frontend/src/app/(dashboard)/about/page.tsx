'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function About() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">About Breakout Screener</h1>
        <p className="text-muted-foreground">
          Learn about the application and technical indicators
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>What is Breakout Screener?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p>
            Breakout Screener is a powerful tool for analyzing NSE stocks using technical indicators
            to identify potential breakout opportunities.
          </p>
          <p>
            The application processes hundreds of stocks from various NSE indices (NIFTY 50, NIFTY 200,
            MIDCAP, etc.) and provides real-time analysis with CPR levels, volume indicators, and candle patterns.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Technical Indicators</CardTitle>
          <CardDescription>
            Understanding the analysis metrics
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">CPR (Central Pivot Range)</h3>
            <p className="text-sm text-muted-foreground">
              CPR levels help identify support and resistance zones. Narrow gap indicates consolidation,
              while wide gap suggests trending market.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Breakout Indicator</h3>
            <p className="text-sm text-muted-foreground">
              Identifies when price breaks above previous highs, suggesting potential upward momentum.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Volume Indicator</h3>
            <p className="text-sm text-muted-foreground">
              Analyzes trading volume relative to historical averages to confirm price movements.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Version Information</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Version 2.0.0 - Phase 5 Complete UI Redesign
          </p>
          <p className="text-sm text-muted-foreground">
            Built with Next.js 15, React 19, shadcn/ui, and Tailwind CSS v4
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
