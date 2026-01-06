'use client';

import { useState } from 'react';
import { useTheme } from 'next-themes';
import { Sun, Moon, Monitor, Trash2, AlertTriangle } from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { clearChartData, clearCompleteData } from '@/services/api';
import toast from 'react-hot-toast';

export default function Settings() {
  const { theme, setTheme } = useTheme();
  const [pivotGap, setPivotGap] = useState<number>(50);
  const [rowsPerPage, setRowsPerPage] = useState<number>(50);
  const [autoRefresh, setAutoRefresh] = useState<boolean>(false);
  const [isClearing, setIsClearing] = useState(false);
  const [isClearingAll, setIsClearingAll] = useState(false);
  const [openClearDialog, setOpenClearDialog] = useState(false);
  const [openClearAllDialog, setOpenClearAllDialog] = useState(false);

  const handleClearCache = async () => {
    setIsClearing(true);
    try {
      await clearChartData();
      toast.success('Cache cleared successfully');
      setOpenClearDialog(false);
    } catch (error) {
      toast.error('Failed to clear cache');
    } finally {
      setIsClearing(false);
    }
  };

  const handleClearAllData = async () => {
    setIsClearingAll(true);
    try {
      await clearCompleteData();
      toast.success('All data cleared successfully');
      setOpenClearAllDialog(false);
    } catch (error) {
      toast.error('Failed to clear all data');
    } finally {
      setIsClearingAll(false);
    }
  };

  const handleSaveSettings = () => {
    // Save settings to localStorage
    localStorage.setItem('pivotGap', pivotGap.toString());
    localStorage.setItem('rowsPerPage', rowsPerPage.toString());
    localStorage.setItem('autoRefresh', autoRefresh.toString());
    toast.success('Settings saved successfully');
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Configure application preferences</p>
      </div>

      {/* Appearance Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Customize theme and display settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            <Label htmlFor="theme">Theme</Label>
            <div className="grid grid-cols-3 gap-3">
              <Button
                variant={theme === 'light' ? 'default' : 'outline'}
                onClick={() => setTheme('light')}
                className="w-full"
              >
                <Sun className="mr-2 h-4 w-4" />
                Light
              </Button>
              <Button
                variant={theme === 'dark' ? 'default' : 'outline'}
                onClick={() => setTheme('dark')}
                className="w-full"
              >
                <Moon className="mr-2 h-4 w-4" />
                Dark
              </Button>
              <Button
                variant={theme === 'system' ? 'default' : 'outline'}
                onClick={() => setTheme('system')}
                className="w-full"
              >
                <Monitor className="mr-2 h-4 w-4" />
                System
              </Button>
            </div>
            <p className="text-sm text-muted-foreground">
              Choose your preferred color theme. System will follow your OS preferences.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Scanner Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Scanner Settings</CardTitle>
          <CardDescription>Configure default scanner parameters</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="pivotGap">Default Pivot Gap (%)</Label>
            <Input
              id="pivotGap"
              type="number"
              value={pivotGap}
              onChange={(e) => setPivotGap(Number(e.target.value))}
              min={0}
              max={1000}
              step={10}
            />
            <p className="text-sm text-muted-foreground">
              Default gap percentage for pivot calculations (0-1000)
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="rowsPerPage">Rows Per Page</Label>
            <Input
              id="rowsPerPage"
              type="number"
              value={rowsPerPage}
              onChange={(e) => setRowsPerPage(Number(e.target.value))}
              min={10}
              max={100}
              step={10}
            />
            <p className="text-sm text-muted-foreground">
              Number of rows to display in the data table (10-100)
            </p>
          </div>

          <div className="flex items-center justify-between space-x-2">
            <div className="space-y-0.5">
              <Label htmlFor="autoRefresh">Auto Refresh</Label>
              <p className="text-sm text-muted-foreground">
                Automatically refresh data every 30 seconds
              </p>
            </div>
            <Switch
              id="autoRefresh"
              checked={autoRefresh}
              onCheckedChange={setAutoRefresh}
            />
          </div>

          <Button onClick={handleSaveSettings} className="w-full">
            Save Scanner Settings
          </Button>
        </CardContent>
      </Card>

      {/* Data Management */}
      <Card>
        <CardHeader>
          <CardTitle>Data Management</CardTitle>
          <CardDescription>Clear cache and manage data</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Dialog open={openClearDialog} onOpenChange={setOpenClearDialog}>
              <DialogTrigger asChild>
                <Button variant="outline" className="w-full">
                  <Trash2 className="mr-2 h-4 w-4" />
                  Clear Chart Data
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Clear Chart Data?</DialogTitle>
                  <DialogDescription>
                    This will clear the current chart data. This action cannot be undone.
                  </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={() => setOpenClearDialog(false)}
                    disabled={isClearing}
                  >
                    Cancel
                  </Button>
                  <Button onClick={handleClearCache} disabled={isClearing}>
                    {isClearing ? 'Clearing...' : 'Clear'}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
            <p className="text-sm text-muted-foreground">
              Remove current session chart data from the database
            </p>
          </div>

          <div className="space-y-2">
            <Dialog open={openClearAllDialog} onOpenChange={setOpenClearAllDialog}>
              <DialogTrigger asChild>
                <Button variant="destructive" className="w-full">
                  <AlertTriangle className="mr-2 h-4 w-4" />
                  Clear All Data
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Clear All Data?</DialogTitle>
                  <DialogDescription>
                    This will permanently delete all data from the database, including
                    historical records. This action cannot be undone.
                  </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={() => setOpenClearAllDialog(false)}
                    disabled={isClearingAll}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={handleClearAllData}
                    disabled={isClearingAll}
                  >
                    {isClearingAll ? 'Clearing...' : 'Delete All Data'}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
            <p className="text-sm text-muted-foreground">
              Permanently delete all data including historical records
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Application Info */}
      <Card>
        <CardHeader>
          <CardTitle>Application Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex justify-between">
            <span className="text-sm text-muted-foreground">Version</span>
            <span className="text-sm font-medium">2.0.0</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-muted-foreground">Build</span>
            <span className="text-sm font-medium">Phase 5.5</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-muted-foreground">Frontend</span>
            <span className="text-sm font-medium">Next.js 15 + React 19</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-muted-foreground">Backend</span>
            <span className="text-sm font-medium">FastAPI + Python</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
