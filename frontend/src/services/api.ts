import { DataResponse } from '@/types/AppInterfaces';
import axiosInstance from '@/utils/axiosInstance';

export const fetchScripts = async (): Promise<DataResponse> => {
  try {
    const response = await axiosInstance.post('/fetch_script_symbols');
    console.log(response);

    return response.data;
  } catch (error) {
    console.error('Error fetching scripts', error);
    throw error;
  }
};
