import { DataResponse, APIResponse, TaskResponse, GeneralResponse } from '@/types/AppInterfaces';
import axiosInstance from '@/utils/axiosInstance';

export const fetchScripts = async (): Promise<APIResponse> => {
  try {
    const response = await axiosInstance.post('/fetch_script_symbols');
    console.log(response.data);

    return response.data;
  } catch (error) {
    console.error('Error fetching scripts', error);
    throw error;
  }
};

export const generateBOData = async (date: string, pivot_val: number): Promise<APIResponse> => {
  try {
    const response = await axiosInstance.post('/generate_bodata', {
      date,
      pivot_val,
    });
    console.log(response.data);

    return response.data;
  } catch (error) {
    console.error('Error fetching scripts', error);
    throw error;
  }
};
export const clearChartData = async (): Promise<APIResponse> => {
  try {
    const response = await axiosInstance.post('/clear_chart');
    console.log(response.data);

    return response.data;
  } catch (error) {
    console.error('Error fetching scripts', error);
    throw error;
  }
};

export const clearCompleteData = async (): Promise<APIResponse> => {
  try {
    const response = await axiosInstance.post('/clear_complete_data');
    console.log(response.data);

    return response.data;
  } catch (error) {
    console.error('Error fetching scripts', error);
    throw error;
  }
};

export const getTaskStatus = async (id: string): Promise<TaskResponse> => {
  try {
    const response = await axiosInstance.get<TaskResponse>(`/task_status/${id}`);
    console.log(response.data);

    console.log('getTaskStatus Response:');
    return response.data;
  } catch (error) {
    console.error('Error fetching task status', error);
    throw error;
  }
};

export const getData = async (page: number, limit: number): Promise<DataResponse> => {
  try {
    const response = await axiosInstance.get<DataResponse>('/get_data', {
      params: {
        page,
        limit,
      },
    });

    console.log('getData Response:');
    console.log(response.data);

    return response.data;
  } catch (error) {
    console.error('Error fetching scripts', error);
    throw error;
  }
};

export const suspendAction = async () => {
  try {
    const response = await axiosInstance.post<GeneralResponse>('/suspend_action');
    return response.data;
  } catch (error) {
    console.error('Error suspending action ${error}');
    throw error;
  }
};
