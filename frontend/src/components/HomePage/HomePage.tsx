import React, { useEffect, useState } from 'react';
import { useAtom } from 'jotai';
import { toast } from 'sonner';
import DataTable from '@/components/DataTable/DataTable';
import InputForm from '@/components/InputForm/InputForm';
import { TaskResponse } from '@/types/AppInterfaces';
import { getTaskStatus, getCurrentTask } from '@/services/api';
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
  scriptsAnalyzedAtom,
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
  const [scriptsAnalyzed, setScriptsAnalyzed] = useAtom(scriptsAnalyzedAtom);

  const [timerInterval, setTimerInterval] = useState<NodeJS.Timeout | null>(null);

  // Check for running task on component mount (after page refresh)
  useEffect(() => {
    const checkForRunningTask = async () => {
      try {
        console.log('Checking for running task on page load...');
        const taskResponse = await getCurrentTask();

        if (taskResponse.task_id && taskResponse.status !== 'NO_ACTIVE_TASK') {
          console.log('Found active task:', taskResponse.task_id);

          // Resume monitoring the task
          setTaskId(taskResponse.task_id);

          // Restore task metadata if available
          if (taskResponse.result) {
            if (taskResponse.result.start_time) {
              setStartTime(taskResponse.result.start_time);
            }
            if (taskResponse.result.current && taskResponse.result.total) {
              setProgress({
                current: taskResponse.result.current,
                total: taskResponse.result.total,
                script: taskResponse.result.script
              });
              // Restore scripts analyzed count
              setScriptsAnalyzed(taskResponse.result.current);
            }
          }

          toast.info('Resumed monitoring active task');
        } else {
          console.log('No active task found');
        }
      } catch (error) {
        console.error('Error checking for running task:', error);
      }
    };

    checkForRunningTask();
  }, []); // Run only once on mount

  useEffect(() => {
    if (taskId) {
      if (timerInterval) {
        clearInterval(timerInterval);
      }

      // Use existing start time if available, otherwise use current time
      const task_start_time = startTime || new Date().toISOString();

      const interval = setInterval(() => {
        const now = new Date().toISOString();
        setRunningTime(formatDuration(task_start_time, now));
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

        // Update start time if available
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
            // Update scripts analyzed count dynamically
            setScriptsAnalyzed(result.current);
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
          // Set final scripts analyzed count
          if (result?.total) {
            setScriptsAnalyzed(result.total);
          }
          setProgress(null);
          setStartRefresh(false);
          setRefreshTrigger(prev => prev + 1); // Force data table refresh
          toast.success('Analysis complete!');
        } else if (status === 'FAILURE') {
          clearInterval(interval);
          clearInterval(timerInterval);
          setProgress(null);
          setStartRefresh(false);
          setRefreshTrigger(prev => prev + 1); // Force data table refresh
          toast.error('Analysis failed!');
        } else {
          // Update start time for other statuses (PENDING, etc.)
          if (result?.start_time) setStartTime(result.start_time);
          setStartRefresh(true);
        }
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
