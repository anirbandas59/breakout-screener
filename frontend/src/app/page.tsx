import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function HomePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center space-y-4 mb-8">
        <h1 className="text-4xl font-bold tracking-tight">
          Breakout Screener V2
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Advanced breakout stock screener with real-time data analysis and comprehensive filtering capabilities
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Real-time Data</CardTitle>
            <CardDescription>
              Live NSE stock data with breakout analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full">View Live Data</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Advanced Filtering</CardTitle>
            <CardDescription>
              Powerful filters for precise stock screening
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full" variant="outline">
              Configure Filters
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Analytics Dashboard</CardTitle>
            <CardDescription>
              Comprehensive charts and performance metrics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full" variant="secondary">
              View Analytics
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="mt-12 text-center">
        <p className="text-sm text-muted-foreground">
          Powered by Next.js 15, React 19, and modern web technologies
        </p>
      </div>
    </div>
  )
}