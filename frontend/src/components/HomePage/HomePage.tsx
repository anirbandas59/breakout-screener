import React, { useEffect, useState } from 'react';
import { useAtom } from 'jotai';
import { toast } from 'sonner';
import DataTable from '@/components/DataTable/DataTable';
import InputForm from '@/components/InputForm/InputForm';
import { TaskResponse } from '@/types/AppInterfaces';
import { getTaskStatus } from '@/services/api';
import { formatDuration, getCurrentDate } from '@/utils/helperFn';
import {
  dateAtom,
  taskIdAtom,
  startRefreshAtom,
  progressAtom,
  startTimeAtom,
  runningTimeAtom,
  scriptFetchedOnAtom,
  refreshTriggerAtom,
} from '@/store/atoms';

const HomePage: React.FC = () => {
  const [date, setDate] = useAtom(dateAtom);
  const [taskId, setTaskId] = useAtom(taskIdAtom);
  const [startRefresh, setStartRefresh] = useAtom(startRefreshAtom);
  const [startTime, setStartTime] = useAtom(startTimeAtom);
  const [runningTime, setRunningTime] = useAtom(runningTimeAtom);
  const [scriptFetchedOn, setScriptFetchedOn] = useAtom(scriptFetchedOnAtom);
  const [progress, setProgress] = useAtom(progressAtom);
  const [refreshTrigger, setRefreshTrigger] = useAtom(refreshTriggerAtom);

  const [timerInterval, setTimerInterval] = useState<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (taskId) {
      const start_time = new Date().toISOString();

      if (timerInterval) {
        clearInterval(timerInterval);
      }

      const interval = setInterval(() => {
        const now = new Date().toISOString();
        setRunningTime(formatDuration(start_time, now));
      }, 1000);

      setTimerInterval(interval);
      pollTaskStatus(taskId, interval);
    }
  }, [taskId]);

  const pollTaskStatus = async (id: string, timerInterval: NodeJS.Timeout) => {
    const interval = setInterval(async () => {
      try {
        const task_response: TaskResponse = await getTaskStatus(id);
        const { status, result } = task_response;
        // console.log(`Task Response: ${task_response}`);
        if (result?.start_time) setStartTime(result.start_time);

        setStartRefresh(true);

        // Handle PROGRESS status
        if (status === 'PROGRESS' && result) {
          if (result.current && result.total) {
            setProgress({
              current: result.current,
              total: result.total,
              script: result.script
            });
          }
        }

        if (status === 'SUCCESS') {
          clearInterval(interval);
          clearInterval(timerInterval);
          console.log(result);

          if (result?.end_time) {
            setScriptFetchedOn(result.end_time);
            setRunningTime(formatDuration(result.start_time, result.end_time));
          }
          setProgress(null);
          setStartRefresh(false);
          setRefreshTrigger(prev => prev + 1); // Force data table refresh
          toast.success('Analysis complete!');
        } else if (status === 'FAILURE') {
          clearInterval(interval); // Stop the timer
          clearInterval(timerInterval); // Stop polling
          setProgress(null);
          setStartRefresh(false);
          setRefreshTrigger(prev => prev + 1); // Force data table refresh
          toast.error('Analysis failed!');
        } else {
          console.log(result);
          if (result?.start_time) setStartTime(result.start_time);

          setStartRefresh(true);
        }
        // return result;
      } catch (error) {
        console.error('Error polling in Task', error);
        clearInterval(interval);
        setProgress(null);
        setStartRefresh(false);
      }
    }, 2000);
  };

  useEffect(() => {
    const today: string = getCurrentDate();
    setDate(today);
  }, [setDate]);

  return (
    <>
      <div>
        <InputForm />

        {/* Progress Bar */}
        {progress && (
          <div className="mx-6 mb-4">
            <div className="w-full bg-muted rounded-full h-3 overflow-hidden">
              <div
                className="bg-primary h-3 transition-all duration-300 ease-in-out"
                style={{ width: `${(progress.current / progress.total) * 100}%` }}
              />
            </div>
            <p className="text-sm mt-2 text-muted-foreground">
              Processing {progress.current} of {progress.total}
              {progress.script && `: ${progress.script}`}
            </p>
          </div>
        )}
      </div>
      <div className="flex-1 my-2">
        <DataTable />
      </div>
    </>
  );
};

export default HomePage;
// const handleDataChange = (data: DataRow[]) => {
//   setData(data);
// };

// const fetchData = async (page: number, limit: number) => {
//   setIsLoading(true);

//   try {
//     const response = await axiosInstance.get<DataResponse>('/get_data', {
//       params: {
//         page,
//         limit,
//       },
//     });

//     // console.log(response.data);
//     const { total } = response.data;

//     // onDataChange(data);
//     setTotalPages(total);
//   } catch (error) {
//     console.error('Error fetching error', error);
//   } finally {
//     setIsLoading(false);
//   }
// };
