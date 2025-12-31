'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function Reports() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Reports</h1>
        <p className="text-muted-foreground">
          View historical breakout analysis data
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Historical Data</CardTitle>
          <CardDescription>
            Coming soon: View and export historical breakout data
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            This page will include date range picker, summary statistics, and data export functionality.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
