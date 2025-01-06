export interface DataRow {
  group_name: string;
  id: number;
  script_name: string;
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  previous_high: number;
  volume: number;
  cpr: number;
  res1: number;
  res2: number;
  supp1: number;
  supp2: number;
  narrow_gap: string;
  link: string;
  breakout_indicator: string;
  candle_indicator: string;
  volume_indicator: string;
}

export interface DataResponse {
  total: number;
  limit: number;
  page: number;
  data: DataRow[];
}

export interface ButtonGroupsProps {
  onStart: () => void;
  onStop: () => void;
  onClear: () => void;
  onFetchList: () => void;
  onClearList: () => void;
}

export interface DataTableProps {
  startRefresh: boolean;
  date: string;
  onScriptsAnalyzed: (value: number) => void;
  // data: DataRow[];
  // onDataChange: (data: DataRow) => void;
}

export interface InputFormProps {
  date: string;
  startTime: string;
  runningTime: string;
  scriptFetchedOn: string;
  scriptsAnalyzed: number;
  onTaskIdChange: (value: string) => void;
  onDateChange: (value: string) => void;
  onStartRefresh: (value: boolean) => void;
}

export interface TaskResponse {
  task_id: string;
  status: string;
  result: {
    status: string;
    message: string | null;
    start_time: string | null;
    end_time: string | null;
  } | null;
  error: string | null;
}

export interface APIResponse {
  task_id: string;
  message: string;
}

export interface GeneralResponse {
  status: string;
  message: string | null;
  error: string | null;
}
