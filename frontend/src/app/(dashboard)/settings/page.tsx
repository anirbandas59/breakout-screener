'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">
          Configure application preferences
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>
            Customize theme and display settings
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Coming soon: Theme toggle, sidebar settings, and display preferences
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Scanner Settings</CardTitle>
          <CardDescription>
            Configure default scanner parameters
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Coming soon: Default pivot gap, rows per page, auto-refresh settings
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Data Management</CardTitle>
          <CardDescription>
            Clear cache and manage data
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Coming soon: Clear cache, clear all data operations
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
