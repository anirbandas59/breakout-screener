import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import DataTable from '@/components/DataTable/DataTable';
import InputForm from '@/components/InputForm/InputForm';
import { DataResponse, DataRow, TaskResponse, TaskProgress } from '@/types/AppInterfaces';
import { getTaskStatus } from '@/services/api';
import { formatDateTime, formatDuration, getCurrentDate } from '@/utils/helperFn';

const HomePage: React.FC = () => {
  // const [data, setData] = useState<DataRow[]>([]);
  // const [totalPages, setTotalPages] = useState(0);
  // const [isLoading, setIsLoading] = useState(false);
  const [date, setDate] = useState('');
  const [taskId, setTaskId] = useState('');
  const [scriptsAnalyzed, setScriptsAnalyzed] = useState(0);
  const [startRefresh, setStartRefresh] = useState(false);
  const [startTime, setStartTime] = useState<string>('');
  const [runningTime, setRunningTime] = useState<string>('');
  const [scriptFetchedOn, setScriptFetchedOn] = useState<string>('');
  const [timerInterval, setTimerInterval] = useState<NodeJS.Timeout | null>(null);
  const [progress, setProgress] = useState<TaskProgress | null>(null);

  // Handlers for root data ==> date, start Refresh
  const handleDateChange = (value: string) => {
    setDate(value);
  };

  const handleScriptsAnalyzed = (value: number) => {
    setScriptsAnalyzed(value);
  };

  const handleStartRefresh = (value: boolean) => {
    setStartRefresh(value);
  };

  const handleTaskIdChange = (value: string) => {
    // console.log('Task ID::', value);
    setTaskId(value);
    const start_time = new Date().toISOString();

    if (timerInterval) {
      clearInterval(timerInterval);
    }

    // Start the timer
    const interval = setInterval(() => {
      const now = new Date().toISOString();
      setRunningTime(formatDuration(start_time, now));
    }, 1000);

    setTimerInterval(interval);

    pollTaskStatus(value, interval);
  };

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
          toast.success('Analysis complete!');
        } else if (status === 'FAILURE') {
          clearInterval(interval); // Stop the timer
          clearInterval(timerInterval); // Stop polling
          setProgress(null);
          setStartRefresh(false);
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

  /***
   * UseEffect functions
   */
  // Runs only in 1st instance
  useEffect(() => {
    const today: string = getCurrentDate();
    // console.log(today);

    setDate(today);
  }, []);

  return (
    <>
      <div className="">
        <InputForm
          date={date}
          startTime={formatDateTime(startTime)}
          runningTime={runningTime}
          scriptFetchedOn={formatDateTime(scriptFetchedOn)}
          scriptsAnalyzed={scriptsAnalyzed}
          onTaskIdChange={handleTaskIdChange}
          onDateChange={handleDateChange}
          onStartRefresh={handleStartRefresh}
        />

        {/* Progress Bar */}
        {progress && (
          <div className="mx-6 mb-4">
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className="bg-blue-600 h-3 transition-all duration-300 ease-in-out"
                style={{ width: `${(progress.current / progress.total) * 100}%` }}
              />
            </div>
            <p className="text-sm mt-2 text-gray-700">
              Processing {progress.current} of {progress.total}
              {progress.script && `: ${progress.script}`}
            </p>
          </div>
        )}
      </div>
      <div className="flex-1 my-2">
        <DataTable
          date={date}
          startRefresh={startRefresh}
          onScriptsAnalyzed={handleScriptsAnalyzed}
        />
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
