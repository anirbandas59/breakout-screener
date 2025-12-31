import { atom } from 'jotai';
import { TaskProgress } from '@/types/AppInterfaces';

// Scanner state atoms
export const dateAtom = atom('');
export const taskIdAtom = atom('');
export const scriptsAnalyzedAtom = atom(0);
export const startRefreshAtom = atom(false);
export const progressAtom = atom<TaskProgress | null>(null);
export const startTimeAtom = atom('');
export const runningTimeAtom = atom('');
export const scriptFetchedOnAtom = atom('');
export const refreshTriggerAtom = atom(0);

// Table state atoms
export const tablePageAtom = atom(1);
export const tableLimitAtom = atom(50);
export const totalRecordsAtom = atom(0);
export const isLoadingAtom = atom(false);

// UI state atoms
export const sidebarCollapsedAtom = atom(false);
