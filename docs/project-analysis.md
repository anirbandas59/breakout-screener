# Breakout Screener - Project Analysis & Improvement Recommendations

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Process Flow Analysis](#process-flow-analysis)
3. [Critical Issues](#critical-issues)
4. [Implementation Plan](#implementation-plan)

---

## Executive Summary

The Breakout Screener is a stock analysis application that identifies breakout patterns from NSE (National Stock Exchange of India) stocks. It fetches real-time data, calculates technical indicators (CPR, pivot points, resistance/support levels), and displays actionable insights for traders.

**Current State**: Functional MVP with critical bottlenecks preventing production use
**Tech Stack**: FastAPI + Next.js + PostgreSQL + Celery/Redis
**Target Users**: Indian stock market traders looking for breakout opportunities

### Key Finding
The application has a **critical scalability issue**: it can only process 5 scripts due to a hardcoded limit, and even removing that limit would result in ~2-3 hour runtime for 500 scripts due to inefficient Selenium-based data fetching.

### Solution
Replace Selenium with yfinance for historical price data fetching. This reduces runtime from **~2.5 hours to ~8 minutes** for 500 scripts.

---

## Process Flow Analysis

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER WORKFLOW                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
     ┌──────────────────────────────┼──────────────────────────────┐
     │                              │                              │
     ▼                              ▼                              ▼
┌─────────────┐            ┌─────────────────┐            ┌─────────────┐
│ FETCH LIST  │            │ GENERATE DATA   │            │ VIEW DATA   │
│             │            │                 │            │             │
│ Scrapes NSE │            │ Runs breakout   │            │ Paginated   │
│ for stock   │            │ analysis on     │            │ table with  │
│ symbols     │            │ selected date   │            │ all results │
└──────┬──────┘            └────────┬────────┘            └─────────────┘
       │                            │
       ▼                            ▼
┌─────────────────┐     ┌─────────────────────────────────────────────────┐
│ Selenium → NSE  │     │              FOR EACH SCRIPT                    │
│ (Keep as-is)    │     │  ┌─────────────────────────────────────────┐   │
│                 │     │  │ Current: Selenium → Yahoo Finance       │   │
│ • Runs once     │     │  │ • Runs 400-500 times                    │   │
│ • ~5 URLs       │     │  │ • ~15-20 sec per script                 │   │
│ • ~2-3 min total│     │  │ • Total: ~2-3 HOURS                     │   │
└─────────────────┘     │  │                                         │   │
                        │  │ Replace with: yfinance library          │   │
                        │  │ • ~0.5-1 sec per script                 │   │
                        │  │ • Total: ~5-10 MINUTES                  │   │
                        │  └─────────────────────────────────────────┘   │
                        └─────────────────────────────────────────────────┘
```

### Two Different Data Sources

| Operation | Data Source | Current Method | Recommended |
|-----------|-------------|----------------|-------------|
| **Symbol List** (Fetch List) | NSE Website | Selenium | **Keep Selenium** |
| **Price Data** (Generate BO) | Yahoo Finance | Selenium | **Use yfinance** |

**Why keep Selenium for NSE?**
- NSE doesn't provide a public API for index constituents
- yfinance cannot fetch NIFTY 50/200 membership lists
- This operation runs once per day (~2-3 minutes total)

**Why replace Selenium with yfinance for price data?**
- This operation runs 400-500 times per analysis
- Selenium: ~15-20 seconds × 500 = ~2-3 hours
- yfinance: ~0.5-1 second × 500 = ~5-10 minutes

---

## Critical Issues

### Issue #1: 5-Script Hardcoded Limit

**Location**: `app/services/generate_bo_data.py:51`
```python
for script in scripts[:5]:  # Only processes 5 scripts!
```

**Fix**: Remove `[:5]` after implementing Issue #2 fix.

---

### Issue #2: New Selenium Browser Per Script

**Location**: `app/services/fetch_scripts.py:124-186`
```python
def fetch_script_historical_data(script_name: str) -> pd.DataFrame:
    driver = get_chrome_driver()  # NEW browser instance every call
    driver.implicitly_wait(10)
    try:
        driver.get(yfin_hist_url)
        # ... scrape table ...
    finally:
        driver.quit()  # Browser destroyed
```

**Impact**:
| Scripts | Time per Script | Total Time |
|---------|-----------------|------------|
| 5 (current) | ~15-20 sec | ~1.5 min |
| 500 | ~15-20 sec | **~2.5 hours** |

**Fix**: Replace with yfinance library
```python
import yfinance as yf

def fetch_script_historical_data(script_name: str) -> pd.DataFrame:
    ticker = yf.Ticker(f"{script_name}.NS")
    return ticker.history(period="1mo")
```

**Result**: 500 scripts × ~1 sec = **~8 minutes**

---

### Issue #3: "Start From" Field Not Connected

**Current State**:
| Layer | Status |
|-------|--------|
| Frontend UI | ✅ Exists (`InputForm.tsx:25`) |
| Frontend API Call | ❌ Not passed (`InputForm.tsx:41`) |
| API Service | ❌ Missing parameter (`api.ts:16`) |
| Backend Model | ❌ Missing field (`generate_bo_request.py`) |
| Service Logic | ❌ Not used (`generate_bo_data.py`) |

**Fix**: Connect the field through all 4 layers.

---

### Issue #4: No Celery Task Timeout

**Location**: `app/celery/__init__.py`

**Risk**: Long-running tasks may get re-queued or killed.

**Fix**: Add timeout configuration
```python
c_app.conf.update(
    task_time_limit=3600,       # 1 hour hard limit (sufficient with yfinance)
    task_soft_time_limit=3300,  # 55 min soft limit
    broker_transport_options={'visibility_timeout': 3600},
)
```

---

### Issue #5: No Progress Tracking

**Current State**: Frontend only knows "PENDING", "STARTED", "SUCCESS", "FAILURE"

**Fix**: Update task state with progress
```python
# In generate_bo_data.py
from celery import current_task

for i, script in enumerate(scripts):
    current_task.update_state(
        state='PROGRESS',
        meta={'current': i + 1, 'total': len(scripts)}
    )
    # ... process script ...
```

---

## Implementation Plan

### Phase 1: Critical Fixes (Required for Production)

| Task | File(s) | Effort |
|------|---------|--------|
| Replace Selenium with yfinance for price data | `fetch_scripts.py` | 1-2 hours |
| Remove 5-script limit | `generate_bo_data.py:51` | 5 min |
| Add Celery task timeout | `celery/__init__.py` | 15 min |
| Add progress tracking | `generate_bo_data.py` | 30 min |

**Estimated Effort**: 2-4 hours
**Result**: 500 scripts in ~8-10 minutes

---

### Phase 2: Complete Features

| Task | File(s) | Effort |
|------|---------|--------|
| Connect "Start From" field | 4 files (frontend + backend) | 2 hours |
| Add retry logic for failed scripts | `fetch_scripts.py` | 1 hour |
| Toast notifications | Frontend components | 1 hour |
| Color-code breakout indicators | `DataTable.tsx` | 30 min |
| Button loading states | `ButtonGroups.tsx` | 1 hour |
| Progress bar in UI | `HomePage.tsx` | 1 hour |

**Estimated Effort**: 1 day

---

### Phase 3: Enhancements

| Task | Effort |
|------|--------|
| Table filtering/sorting | 4 hours |
| Export to CSV | 2 hours |
| Date picker calendar | 1 hour |
| Sticky table header | 30 min |
| Sidebar layout (match wireframe) | 8 hours |
| Historical analysis view | 4 hours |

**Estimated Effort**: 2-3 days

---

## Summary

### Root Cause
The application cannot process 500 scripts because:
1. **Hardcoded 5-script limit** - Easy to remove
2. **Selenium for price data** - 20 seconds per script = 2.7 hours for 500
3. **No task timeout** - Long tasks get killed/duplicated

### Solution
Replace Selenium with yfinance for historical price data fetching (NOT for NSE symbol fetching).

### Correct Tool for Each Job

| Task | Tool | Reason |
|------|------|--------|
| Fetch NIFTY 50/200 symbols | Selenium → NSE | No API available, runs once |
| Fetch historical prices | yfinance | Fast, reliable, runs 500× |
