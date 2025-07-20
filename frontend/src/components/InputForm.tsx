'use client'

import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { format } from 'date-fns'
import { CalendarIcon } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

// Validation schema
const analysisFormSchema = z.object({
  analysisDate: z.string().min(1, 'Analysis date is required'),
  pivotGap: z
    .number()
    .min(0.1, 'Pivot gap must be at least 0.1%')
    .max(10, 'Pivot gap cannot exceed 10%'),
  startFrom: z
    .number()
    .int()
    .min(1, 'Start from must be at least 1')
    .optional()
    .default(1),
})

type AnalysisFormData = z.infer<typeof analysisFormSchema>

interface InputFormProps {
  analysisDate: string
  startTime?: string
  runningTime?: string
  scriptFetchedOn?: string
  scriptsAnalyzed: number
  onSubmit: (data: AnalysisFormData) => void
  onDateChange: (date: string) => void
  isAnalysisRunning?: boolean
}

export default function InputForm({
  analysisDate,
  startTime,
  runningTime,
  scriptFetchedOn,
  scriptsAnalyzed,
  onSubmit,
  onDateChange,
  isAnalysisRunning = false,
}: InputFormProps) {
  const form = useForm<AnalysisFormData>({
    resolver: zodResolver(analysisFormSchema),
    defaultValues: {
      analysisDate,
      pivotGap: 0.5,
      startFrom: 1,
    },
  })

  const handleFormSubmit = (data: AnalysisFormData) => {
    onSubmit(data)
    onDateChange(data.analysisDate)
  }

  const watchedDate = form.watch('analysisDate')

  // Update form when external date changes
  React.useEffect(() => {
    if (analysisDate && analysisDate !== watchedDate) {
      form.setValue('analysisDate', analysisDate)
    }
  }, [analysisDate, watchedDate, form])

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Analysis Configuration</CardTitle>
        <CardDescription>
          Set up parameters for breakout analysis
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleFormSubmit)} className="space-y-6">
            {/* Input Fields Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <FormField
                control={form.control}
                name="analysisDate"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Analysis Date</FormLabel>
                    <FormControl>
                      <Input
                        type="date"
                        {...field}
                        disabled={isAnalysisRunning}
                        className="w-full"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="pivotGap"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Pivot Gap (%)</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.1"
                        min="0.1"
                        max="10"
                        {...field}
                        onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                        disabled={isAnalysisRunning}
                        className="w-full"
                      />
                    </FormControl>
                    <FormDescription>
                      Breakout threshold percentage
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="startFrom"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Start From</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min="1"
                        {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value) || 1)}
                        disabled={isAnalysisRunning}
                        className="w-full"
                      />
                    </FormControl>
                    <FormDescription>
                      Starting stock index
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* Analysis Status Section */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold mb-4">Analysis Status</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="space-y-2">
                  <Label className="text-sm font-medium text-muted-foreground">
                    Scripts Analyzed
                  </Label>
                  <div className="text-2xl font-bold text-primary">
                    {scriptsAnalyzed.toLocaleString()}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="text-sm font-medium text-muted-foreground">
                    Start Time
                  </Label>
                  <div className="text-sm">
                    {startTime || '--:--:--'}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="text-sm font-medium text-muted-foreground">
                    Running Time
                  </Label>
                  <div className="text-sm font-mono">
                    {runningTime || '--:--:--'}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="text-sm font-medium text-muted-foreground">
                    Completed At
                  </Label>
                  <div className="text-sm">
                    {scriptFetchedOn || '--'}
                  </div>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex justify-end">
              <Button
                type="submit"
                disabled={isAnalysisRunning || !form.formState.isValid}
                className="min-w-[120px]"
              >
                {isAnalysisRunning ? 'Running...' : 'Start Analysis'}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}