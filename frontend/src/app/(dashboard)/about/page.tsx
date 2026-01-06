'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  TrendingUp,
  BarChart3,
  Activity,
  Target,
  Zap,
  Shield,
  Github,
  FileText,
} from 'lucide-react';

export default function About() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">About Breakout Screener</h1>
        <p className="text-muted-foreground">
          Learn about the application and technical indicators
        </p>
      </div>

      {/* Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            What is Breakout Screener?
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="leading-relaxed">
            Breakout Screener is a powerful tool for analyzing NSE (National Stock Exchange)
            stocks using advanced technical indicators to identify potential breakout
            opportunities. The application processes hundreds of stocks from various NSE
            indices including NIFTY 50, NIFTY 200, MIDCAP, and more.
          </p>
          <p className="leading-relaxed">
            Built with modern web technologies, this application provides real-time analysis
            with Central Pivot Range (CPR) levels, volume indicators, and candle pattern
            recognition to help traders make informed decisions.
          </p>
          <div className="flex flex-wrap gap-2 pt-2">
            <Badge variant="success">
              <Zap className="mr-1 h-3 w-3" />
              Real-time Analysis
            </Badge>
            <Badge variant="default">
              <BarChart3 className="mr-1 h-3 w-3" />
              500+ Stocks
            </Badge>
            <Badge variant="warning">
              <Shield className="mr-1 h-3 w-3" />
              Professional Grade
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Technical Indicators */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Technical Indicators
          </CardTitle>
          <CardDescription>Understanding the analysis metrics</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <div className="mt-1">
                <Target className="h-5 w-5 text-primary" />
              </div>
              <div className="space-y-1 flex-1">
                <h3 className="font-semibold">CPR (Central Pivot Range)</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  CPR levels help identify support and resistance zones for the trading day.
                  A <strong>narrow gap</strong> between TC (Top Central) and BC (Bottom
                  Central) indicates consolidation, suggesting a potential breakout. A{' '}
                  <strong>wide gap</strong> suggests a trending market with clear direction.
                </p>
                <div className="grid grid-cols-2 gap-2 pt-2">
                  <div className="text-xs">
                    <span className="font-medium">CPR:</span> Central Pivot
                  </div>
                  <div className="text-xs">
                    <span className="font-medium">R1/R2:</span> Resistance Levels
                  </div>
                  <div className="text-xs">
                    <span className="font-medium">S1/S2:</span> Support Levels
                  </div>
                  <div className="text-xs">
                    <span className="font-medium">Gap:</span> TC - BC difference
                  </div>
                </div>
              </div>
            </div>

            <Separator />

            <div className="flex items-start gap-3">
              <div className="mt-1">
                <TrendingUp className="h-5 w-5 text-success" />
              </div>
              <div className="space-y-1 flex-1">
                <h3 className="font-semibold">Breakout Indicator</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Identifies when price action breaks above previous highs, suggesting
                  potential upward momentum. Different breakout types include:
                </p>
                <ul className="text-sm space-y-1 pt-2">
                  <li className="flex items-center gap-2">
                    <Badge variant="success" className="text-xs">
                      BREAKOUT
                    </Badge>
                    <span className="text-muted-foreground">
                      Price breaks above previous high
                    </span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Badge variant="default" className="text-xs">
                      NO_BREAKOUT
                    </Badge>
                    <span className="text-muted-foreground">
                      Price within normal range
                    </span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Badge variant="danger" className="text-xs">
                      RED_CANDLE
                    </Badge>
                    <span className="text-muted-foreground">Bearish candle pattern</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Badge variant="warning" className="text-xs">
                      BIG_SELL_WICK
                    </Badge>
                    <span className="text-muted-foreground">
                      Large selling pressure detected
                    </span>
                  </li>
                </ul>
              </div>
            </div>

            <Separator />

            <div className="flex items-start gap-3">
              <div className="mt-1">
                <Activity className="h-5 w-5 text-warning" />
              </div>
              <div className="space-y-1 flex-1">
                <h3 className="font-semibold">Candle Indicator</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Analyzes the daily candle pattern to determine bullish or bearish sentiment:
                </p>
                <ul className="text-sm space-y-1 pt-2">
                  <li className="flex items-center gap-2">
                    <Badge variant="success" className="text-xs">
                      GREEN_CANDLE
                    </Badge>
                    <span className="text-muted-foreground">
                      Bullish - Close &gt; Open
                    </span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Badge variant="danger" className="text-xs">
                      RED_CANDLE
                    </Badge>
                    <span className="text-muted-foreground">Bearish - Close &lt; Open</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Badge variant="default" className="text-xs">
                      DOJI
                    </Badge>
                    <span className="text-muted-foreground">
                      Neutral - Open ≈ Close (indecision)
                    </span>
                  </li>
                </ul>
              </div>
            </div>

            <Separator />

            <div className="flex items-start gap-3">
              <div className="mt-1">
                <BarChart3 className="h-5 w-5 text-primary" />
              </div>
              <div className="space-y-1 flex-1">
                <h3 className="font-semibold">Volume Indicator</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Analyzes trading volume relative to historical averages to confirm price
                  movements and gauge market participation:
                </p>
                <ul className="text-sm space-y-1 pt-2">
                  <li className="flex items-center gap-2">
                    <Badge variant="success" className="text-xs">
                      GOOD
                    </Badge>
                    <span className="text-muted-foreground">
                      High volume - Strong conviction
                    </span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Badge variant="warning" className="text-xs">
                      AVERAGE
                    </Badge>
                    <span className="text-muted-foreground">Normal trading activity</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Badge variant="default" className="text-xs">
                      LOW
                    </Badge>
                    <span className="text-muted-foreground">
                      Low volume - Weak participation
                    </span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Technology Stack */}
      <Card>
        <CardHeader>
          <CardTitle>Technology Stack</CardTitle>
          <CardDescription>Modern technologies powering the application</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-3">
              <h3 className="font-semibold text-sm">Frontend</h3>
              <ul className="text-sm space-y-2 text-muted-foreground">
                <li>• Next.js 15 with App Router</li>
                <li>• React 19 with Server Components</li>
                <li>• TypeScript for type safety</li>
                <li>• shadcn/ui component library</li>
                <li>• Tailwind CSS v4</li>
                <li>• TanStack Table for data grids</li>
                <li>• Jotai for state management</li>
              </ul>
            </div>
            <div className="space-y-3">
              <h3 className="font-semibold text-sm">Backend</h3>
              <ul className="text-sm space-y-2 text-muted-foreground">
                <li>• FastAPI (Python)</li>
                <li>• PostgreSQL database</li>
                <li>• Celery for async tasks</li>
                <li>• Redis for task queue</li>
                <li>• yfinance for market data</li>
                <li>• Pydantic for validation</li>
                <li>• SQLAlchemy ORM</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Version Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Version Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Current Version</span>
            <Badge>v2.0.0</Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Build Phase</span>
            <Badge variant="success">Phase 5.5 - Complete UI Redesign</Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Release Date</span>
            <span className="text-sm font-medium">January 2026</span>
          </div>

          <Separator className="my-4" />

          <div className="space-y-2">
            <h3 className="font-semibold text-sm">Key Features</h3>
            <ul className="text-sm space-y-1 text-muted-foreground">
              <li>✓ Process 500+ NSE stocks in ~10-15 minutes</li>
              <li>✓ Real-time progress tracking with live updates</li>
              <li>✓ Advanced filtering and search capabilities</li>
              <li>✓ CSV export for external analysis</li>
              <li>✓ Dark mode support with theme persistence</li>
              <li>✓ Responsive design for all screen sizes</li>
              <li>✓ Professional UI with shadcn/ui components</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Additional Resources */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Github className="h-5 w-5" />
            Resources & Documentation
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">
            For technical documentation, development guides, and project updates, please
            refer to the project repository and documentation files.
          </p>
          <div className="grid gap-2">
            <div className="flex items-center gap-2 text-sm">
              <FileText className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">PLAN.md - Project strategy</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <FileText className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">
                INSTRUCTIONS.md - Implementation tasks
              </span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <FileText className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">
                CLAUDE.md - Development guide
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
