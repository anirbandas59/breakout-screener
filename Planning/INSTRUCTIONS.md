# Implementation Instructions

**For**: Developer Agent
**From**: Project Manager (PM)
**Last Updated**: 2024-12-22

---

## How to Use This File

1. Work through tasks in order (Phase 1 → Phase 2 → etc.)
2. Update checkbox when task is done: `[ ]` → `[x]`
3. If blocked, mark with `[?]` and write in COMMS.md
4. PM will verify and mark `[✓]` when approved

**Status Legend**:
- `[ ]` Not started
- `[x]` Completed by developer
- `[✓]` Verified by PM
- `[?]` Blocked/needs help
- `[!]` Failed, needs rework

---

## Phase 1: Critical Backend Fixes

### Task 1.1: Replace Selenium with yfinance for Price Data

**File**: `app/services/fetch_scripts.py`

**Current Code** (lines 124-186):
```python
def fetch_script_historical_data(script_name: str) -> pd.DataFrame:
    driver = get_chrome_driver()  # SLOW - new browser each call
    # ... selenium scraping ...
```

**New Code**:
```python
import yfinance as yf

def fetch_script_historical_data(script_name: str, period: str = "1mo") -> pd.DataFrame:
    """
    Fetch historical OHLCV data using yfinance.

    Args:
        script_name: NSE stock symbol (e.g., "RELIANCE")
        period: Data period (default "1mo" for 1 month)

    Returns:
        DataFrame with Date index and OHLCV columns
    """
    try:
        ticker = yf.Ticker(f"{script_name}.NS")
        df = ticker.history(period=period)

        if df.empty:
            logging.warning(f"No data returned for {script_name}")
            return pd.DataFrame()

        # Ensure column names match expected format
        df.index = df.index.strftime('%Y-%m-%d')
        return df

    except Exception as e:
        logging.error(f"Error fetching data for {script_name}: {e}")
        return pd.DataFrame()
```

**Steps**:
- [ ] Add `yfinance` to requirements.txt
- [ ] Replace `fetch_script_historical_data` function
- [ ] Remove unused Selenium imports (keep for NSE scraping)
- [ ] Test with single script: `RELIANCE`
- [ ] Test with 10 scripts
- [x] **Developer Done**
- [ ] **PM Verified**

**Notes**:
```
Developer: (write notes here)
PM: (review notes here)
```

---

### Task 1.2: Remove 5-Script Limit

**File**: `app/services/generate_bo_data.py`

**Current Code** (line 51):
```python
for script in scripts[:5]:
```

**New Code**:
```python
for script in scripts:
```

**Steps**:
- [ ] Remove `[:5]` slice
- [ ] Test with full dataset
- [x] **Developer Done**
- [ ] **PM Verified**

**Notes**:
```
Developer: (write notes here)
PM: (review notes here)
```

---

### Task 1.3: Add Celery Task Timeout

**File**: `app/celery/__init__.py`

**Add after celery_app initialization**:
```python
celery_app.conf.update(
    task_time_limit=3600,           # 1 hour hard limit
    task_soft_time_limit=3300,      # 55 min soft limit
    broker_transport_options={
        'visibility_timeout': 3600   # 1 hour
    },
    task_acks_late=True,            # Ack after completion
    task_reject_on_worker_lost=True # Requeue if worker dies
)
```

**Steps**:
- [ ] Add timeout configuration
- [ ] Verify Celery worker starts without errors
- [x] **Developer Done**
- [ ] **PM Verified**

**Notes**:
```
Developer: (write notes here)
PM: (review notes here)
```

---

### Task 1.4: Add Progress Tracking

**File**: `app/services/generate_bo_data.py`

**Modify the function signature and loop**:
```python
from celery import current_task

def generate_BOData(db: Session, analysis_date: str, pivot_val: float) -> dict:
    # ... existing setup code ...

    scripts = db.query(BreakoutData).all()
    total_scripts = len(scripts)

    for i, script in enumerate(scripts):
        # Update progress
        if current_task:
            current_task.update_state(
                state='PROGRESS',
                meta={
                    'current': i + 1,
                    'total': total_scripts,
                    'script': script.script_name
                }
            )

        # Check suspension
        if SUSPEND_ANALYSIS.is_set():
            return {
                "status": "SUSPENDED",
                "message": f"Suspended at script {i + 1} of {total_scripts}"
            }

        # ... rest of processing ...

    return {
        "status": "SUCCESS",
        "message": f"Completed {total_scripts} scripts"
    }
```

**Steps**:
- [ ] Import `current_task` from celery
- [ ] Add progress update in loop
- [ ] Update return message with count
- [ ] Test progress appears in task status
- [x] **Developer Done**
- [ ] **PM Verified**

**Notes**:
```
Developer: (write notes here)
PM: (review notes here)
```

---

### Task 1.5: Add Retry Logic

**File**: `app/services/fetch_scripts.py`

**Add retry decorator**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.RequestException, Exception)),
    before_sleep=lambda retry_state: logging.warning(
        f"Retrying {retry_state.fn.__name__}, attempt {retry_state.attempt_number}"
    )
)
def fetch_script_historical_data(script_name: str, period: str = "1mo") -> pd.DataFrame:
    # ... existing yfinance code ...
```

**Steps**:
- [ ] Add `tenacity` to requirements.txt
- [ ] Add retry decorator to fetch function
- [ ] Test retry works (disconnect network briefly)
- [x] **Developer Done**
- [ ] **PM Verified**

**Notes**:
```
Developer: (write notes here)
PM: (review notes here)
```

---

## Phase 1 Completion Checklist

- [ ] All 5 tasks completed
- [ ] Test: Process 50 scripts successfully
- [ ] Test: Process 500 scripts successfully
- [ ] Test: Progress tracking visible
- [ ] Test: Task timeout works
- [ ] **Phase 1 Approved by PM**

---

## Phase 2: Connect Missing Features

### Task 2.1: Connect "Start From" Field

**Files to modify**:
1. `app/models/generate_bo_request.py`
2. `app/routers/routes.py`
3. `app/services/generate_bo_data.py`
4. `frontend/src/services/api.ts`
5. `frontend/src/components/InputForm/InputForm.tsx`

**Step 2.1.1 - Backend Model**:
```python
# app/models/generate_bo_request.py
from pydantic import BaseModel, Field

class GenerateBODataRequest(BaseModel):
    date: str
    pivot_val: float = Field(default=0.5, ge=0, le=10)
    start_from: int = Field(default=1, ge=1)
```

**Step 2.1.2 - Backend Route**:
```python
# app/routers/routes.py - modify generate_bodata
@router.post("/generate_bodata")
def generate_bodata(request: GenerateBODataRequest):
    task = generate_bo_data_task.apply_async(
        args=[request.date, request.pivot_val, request.start_from]
    )
    return {"task_id": task.id, "message": "Started"}
```

**Step 2.1.3 - Backend Service**:
```python
# app/services/generate_bo_data.py
def generate_BOData(db: Session, analysis_date: str, pivot_val: float, start_from: int = 1) -> dict:
    scripts = db.query(BreakoutData).all()
    scripts_to_process = scripts[start_from - 1:]  # 1-indexed to 0-indexed
    # ... rest of code ...
```

**Step 2.1.4 - Celery Task**:
```python
# app/tasks/__init__.py
@celery_app.task
def generate_bo_data_task(date, pivot, start_from=1):
    # ... update to pass start_from ...
```

**Step 2.1.5 - Frontend API**:
```typescript
// frontend/src/services/api.ts
export const generateBOData = async (
  date: string,
  pivot_val: number,
  start_from: number = 1
): Promise<APIResponse> => {
  const response = await axiosInstance.post('/generate_bodata', {
    date,
    pivot_val,
    start_from,
  });
  return response.data;
};
```

**Step 2.1.6 - Frontend Component**:
```typescript
// frontend/src/components/InputForm/InputForm.tsx
const handleStart = async () => {
  const result = await generateBOData(date, pivotGap / 100, startFrom);
  onTaskIdChange(result.task_id);
};
```

**Steps**:
- [ ] Update Pydantic model with start_from
- [ ] Update route to accept start_from
- [ ] Update service to use start_from
- [ ] Update Celery task signature
- [ ] Update frontend API function
- [ ] Update frontend to pass startFrom
- [ ] Test: Start from 1, verify all processed
- [ ] Test: Start from 50, verify skip first 49
- [x] **Developer Done**
- [ ] **PM Verified**

**Notes**:
```
Developer: (write notes here)
PM: (review notes here)
```

---

### Task 2.2: Add Toast Notifications

**File**: `frontend/src/components/InputForm/InputForm.tsx`

**Install**:
```bash
cd frontend && npm install react-hot-toast
```

**Add to layout** (`frontend/src/app/layout.tsx`):
```tsx
import { Toaster } from 'react-hot-toast';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Toaster position="top-right" />
      </body>
    </html>
  );
}
```

**Update handlers**:
```tsx
import toast from 'react-hot-toast';

const handleStart = async () => {
  try {
    const result = await generateBOData(date, pivotGap / 100, startFrom);
    onTaskIdChange(result.task_id);
    toast.success('Analysis started!');
  } catch (error) {
    toast.error('Failed to start analysis');
  }
};

const handleFetchList = async () => {
  try {
    const result = await fetchScripts();
    onTaskIdChange(result.task_id);
    toast.success('Fetching stock list...');
  } catch (error) {
    toast.error('Failed to fetch stock list');
  }
};
```

**Steps**:
- [ ] Install react-hot-toast
- [ ] Add Toaster to layout
- [ ] Add toast to all handlers (Start, Stop, Clear, Fetch, Clear List)
- [ ] Test: See success/error toasts
- [x] **Developer Done**
- [ ] **PM Verified**

**Notes**:
```
Developer: (write notes here)
PM: (review notes here)
```

---

### Task 2.3: Update Frontend Progress Display

**File**: `frontend/src/components/HomePage/HomePage.tsx`

**Update task status handling**:
```tsx
interface TaskProgress {
  current: number;
  total: number;
  script?: string;
}

const [progress, setProgress] = useState<TaskProgress | null>(null);

// In pollTaskStatus function:
const pollTaskStatus = async () => {
  const status = await getTaskStatus(taskId);

  if (status.status === 'PROGRESS' && status.result) {
    setProgress({
      current: status.result.current,
      total: status.result.total,
      script: status.result.script
    });
  }

  if (status.status === 'SUCCESS') {
    setProgress(null);
    toast.success('Analysis complete!');
  }
};
```

**Add progress bar component**:
```tsx
{progress && (
  <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
    <div
      className="bg-blue-600 h-2 rounded-full transition-all"
      style={{ width: `${(progress.current / progress.total) * 100}%` }}
    />
    <p className="text-sm mt-1">
      Processing {progress.current} of {progress.total}: {progress.script}
    </p>
  </div>
)}
```

**Steps**:
- [ ] Add progress state
- [ ] Handle PROGRESS status in polling
- [ ] Add progress bar UI
- [ ] Test: Progress updates during analysis
- [x] **Developer Done**
- [ ] **PM Verified**

**Notes**:
```
Developer: (write notes here)
PM: (review notes here)
```

---

## Phase 2 Completion Checklist

- [ ] Start From field works
- [ ] Toast notifications appear
- [ ] Progress bar shows during analysis
- [ ] **Phase 2 Approved by PM**

---

## Phase 3: Code Structure (Optional)

*To be detailed after Phase 1 & 2 completion*

---

## Phase 4: Frontend Enhancements (Optional)

*To be detailed after Phase 3 completion*

---

## Quick Reference

### Files Modified in Phase 1
- `requirements.txt` (add yfinance, tenacity)
- `app/services/fetch_scripts.py`
- `app/services/generate_bo_data.py`
- `app/celery/__init__.py`

### Files Modified in Phase 2
- `app/models/generate_bo_request.py`
- `app/routers/routes.py`
- `app/services/generate_bo_data.py`
- `app/tasks/__init__.py`
- `frontend/src/services/api.ts`
- `frontend/src/components/InputForm/InputForm.tsx`
- `frontend/src/components/HomePage/HomePage.tsx`
- `frontend/src/app/layout.tsx`
- `frontend/package.json` (add react-hot-toast)

### Test Commands
```bash
# Backend
cd /home/anirban/workspace/projects/breakout-screener
source venv/bin/activate
pytest app/tests/

# Frontend
cd frontend
npm run build
npm run lint
```
