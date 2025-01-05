import React, { useEffect, useState } from 'react';
import DataTable from '@/components/DataTable/DataTable';
import InputForm from '@/components/InputForm/InputForm';
import { DataResponse, DataRow, TaskResponse } from '@/types/AppInterfaces';
import axiosInstance from '@/utils/axiosInstance';
import { getCurrentDate } from '@/utils/helperFn';

const HomePage: React.FC = () => {
  // const [data, setData] = useState<DataRow[]>([]);
  // const [totalPages, setTotalPages] = useState(0);
  // const [isLoading, setIsLoading] = useState(false);
  const [date, setDate] = useState('');
  const [taskId, setTaskId] = useState('');
  const [startRefresh, setStartRefresh] = useState(false);

  // Handlers for root data ==> date, start Refresh
  const handleDateChange = (value: string) => {
    setDate(value);
  };

  const handleStartRefresh = (value: boolean) => {
    setStartRefresh(value);
  };

  const handleTaskIdChange = (value: string) => {
    setTaskId(value);
    console.log('Task ID::', taskId);

    pollTaskStatus(value);
  };

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

  const pollTaskStatus = async (id: string) => {
    const interval = setInterval(async () => {
      try {
        const task_response = await axiosInstance.get<TaskResponse>(`/task_status/${id}`);
        console.log(`Task Response: ${task_response}`);

        const { status, result } = task_response.data;

        setStartRefresh(true);

        if (status === 'SUCCESS') {
          clearInterval(interval);
          setStartRefresh(false);
          console.log(result);
        }
      } catch (error) {
        console.error('Error polling in Task', error);
        clearInterval(interval);
        setStartRefresh(false);
      }
    }, 30000);
  };

  /***
   * UseEffect functions
   */
  // Runs only in 1st instance
  useEffect(() => {
    const today: string = getCurrentDate();
    console.log(today);

    setDate(today);
  }, []);

  return (
    <>
      <div className="">
        <InputForm
          date={date}
          onTaskIdChange={handleTaskIdChange}
          onDateChange={handleDateChange}
          onStartRefresh={handleStartRefresh}
        />
      </div>
      <div className="flex-1 my-2">
        <DataTable date={date} startRefresh={startRefresh} />
      </div>
    </>
  );
};

export default HomePage;
