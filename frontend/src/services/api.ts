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

export const generateBOData = async (date: string, pivot_val: number, start_from: number = 1): Promise<APIResponse> => {
  try {
    const response = await axiosInstance.post('/generate_bodata', {
      date,
      pivot_val,
      start_from,
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

export const getData = async (
  page: number,
  limit: number,
  search?: string,
  breakoutFilters?: string[]
): Promise<DataResponse> => {
  try {
    const params: any = {
      page,
      limit,
    };

    // Only include search and breakout_filters if they have values
    if (search) {
      params.search = search;
    }
    if (breakoutFilters && breakoutFilters.length > 0) {
      params.breakout_filters = breakoutFilters;
    }

    const response = await axiosInstance.get<DataResponse>('/get_data', {
      params,
      paramsSerializer: {
        // Use 'repeat' format for arrays: ?key=val1&key=val2 instead of ?key[]=val1&key[]=val2
        indexes: null, // This tells axios to use repeat format for arrays
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

export const getCurrentTask = async (): Promise<TaskResponse> => {
  try {
    const response = await axiosInstance.get<TaskResponse>('/current_task');
    console.log('getCurrentTask Response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching current task', error);
    throw error;
  }
};
