# Developer Workflow Guide

**For**: Developer Agent (Claude)
**From**: Project Manager (PM)
**Project**: Breakout Screener V1/V2 Merge

---

## Your Role

You are a Developer Agent responsible for implementing code changes according to the PM's plan. You will:

1. Read and follow instructions from this folder
2. Implement changes to the codebase
3. Test your changes
4. Update checklists and communicate progress
5. Commit code to the `bo_fix_v2` branch

---

## Folder Contents

| File | Purpose | Your Action |
|------|---------|-------------|
| `PLAN.md` | Overall strategy | Read to understand goals |
| `INSTRUCTIONS.md` | Detailed tasks with checklists | Follow step-by-step, update checkboxes |
| `COMMS.md` | Communication log | Write status updates, ask questions |
| `DEVELOPER_INSTRUCTIONS.md` | This file | Your workflow guide |

---

## Workflow Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Read Instructions                                       │
│                                                                 │
│ • Open Planning/INSTRUCTIONS.md                                 │
│ • Find the next uncompleted task [ ]                           │
│ • Read the task description and code snippets                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Implement Changes                                       │
│                                                                 │
│ • Locate the file(s) to modify                                 │
│ • Make the changes as specified                                │
│ • Follow the code examples provided                            │
│ • Keep changes minimal and focused                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Test Your Changes                                       │
│                                                                 │
│ • Run the specific tests mentioned in the task                 │
│ • Verify the feature works as expected                         │
│ • Check for regressions in related functionality               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Update Checklist                                        │
│                                                                 │
│ • In INSTRUCTIONS.md, mark completed steps: [ ] → [x]          │
│ • Write notes in the task's Notes section                      │
│ • Mark "[x] Developer Done" for the task                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Communicate Status                                      │
│                                                                 │
│ • Add entry to COMMS.md with [DEV] tag                         │
│ • Include: what was done, tests passed, any issues             │
│ • Ask questions if blocked                                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: Commit Changes                                          │
│                                                                 │
│ • Stage modified files                                         │
│ • Commit with descriptive message                              │
│ • Do NOT push to main branch                                   │
│ • Stay on bo_fix_v2 branch                                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: Wait for PM Review                                      │
│                                                                 │
│ • PM will review your code and checklist                       │
│ • PM will mark [✓] if approved                                 │
│ • PM may request changes via COMMS.md                          │
│ • Proceed to next task when approved                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Checklist Status Markers

Use these markers in INSTRUCTIONS.md:

| Marker | Meaning | Who Sets It |
|--------|---------|-------------|
| `[ ]` | Not started | Default |
| `[x]` | Completed | Developer |
| `[✓]` | Verified/Approved | PM |
| `[?]` | Blocked/Need help | Developer |
| `[!]` | Failed/Needs rework | PM |

---

## Git Workflow

### Branch Rules
- **Work on**: `bo_fix_v2` branch only
- **Never commit to**: `main` branch
- **Never push to**: `origin/main`

### Commit Messages
Keep them short and descriptive:
```
Task 1.1: Replace Selenium with yfinance
Task 1.2: Remove 5-script limit
Task 2.1: Connect Start From field
```

### Commit Commands
```bash
git add <files>
git commit -m "Task X.X: Brief description"
```

---

## Communication Guidelines

### When to Write in COMMS.md

1. **After completing a task** - Status update
2. **When blocked** - Ask for help
3. **When finding issues** - Report problems
4. **When unsure** - Clarify requirements

### Status Update Template

```markdown
### [DATE] [DEV] Completed Task X.X

**Task**: [Task name]
**Status**: Complete

**Changes Made**:
- `file1.py`: Added yfinance import, replaced function
- `file2.py`: Updated function call

**Testing**:
- [x] Single script test passed
- [x] 10 script test passed

**Issues Encountered**:
- None

**Next**: Moving to Task X.X
```

### Asking for Help Template

```markdown
### [DATE] [DEV] Blocked on Task X.X

**Task**: [Task name]
**Status**: Blocked

**Issue**:
Describe what's not working

**What I Tried**:
1. First attempt
2. Second attempt

**Error Message** (if any):
```
paste error here
```

**Question**:
Specific question for PM

**Blocking**: Yes
```

---

## Testing Guidelines

### Before Marking Task Complete

1. **Unit Test**: Does the specific change work?
2. **Integration Test**: Does it work with other components?
3. **Regression Test**: Did it break anything else?

### Quick Test Commands

```bash
# Backend - run from project root
source venv/bin/activate
python -c "from app.services.fetch_scripts import fetch_script_historical_data; print(fetch_script_historical_data('RELIANCE'))"

# Frontend - run from frontend/
npm run build  # Check for errors
npm run lint   # Check code quality

# Full backend test
pytest app/tests/ -v
```

---

## File Locations Reference

### Backend Files
```
/home/anirban/workspace/projects/breakout-screener/
├── app/
│   ├── services/
│   │   ├── fetch_scripts.py      # Task 1.1, 1.5
│   │   └── generate_bo_data.py   # Task 1.2, 1.4, 2.1
│   ├── celery/
│   │   └── __init__.py           # Task 1.3
│   ├── tasks/
│   │   └── __init__.py           # Task 2.1
│   ├── models/
│   │   └── generate_bo_request.py # Task 2.1
│   └── routers/
│       └── routes.py             # Task 2.1
├── requirements.txt              # Task 1.1, 1.5
└── Planning/                     # This folder
```

### Frontend Files
```
/home/anirban/workspace/projects/breakout-screener/frontend/
├── src/
│   ├── app/
│   │   └── layout.tsx            # Task 2.2
│   ├── components/
│   │   ├── InputForm/
│   │   │   └── InputForm.tsx     # Task 2.1, 2.2
│   │   └── HomePage/
│   │       └── HomePage.tsx      # Task 2.3
│   └── services/
│       └── api.ts                # Task 2.1
└── package.json                  # Task 2.2
```

---

## Common Issues & Solutions

### Issue: yfinance returns empty DataFrame
**Solution**: Check if `.NS` suffix is added to symbol
```python
ticker = yf.Ticker(f"{script_name}.NS")  # .NS for NSE
```

### Issue: Celery task not updating state
**Solution**: Ensure `bind=True` is not used, use `current_task` instead
```python
from celery import current_task
current_task.update_state(state='PROGRESS', meta={...})
```

### Issue: Frontend not receiving progress
**Solution**: Check task status endpoint returns `result` field
```python
# In routes.py task_status endpoint
return {"status": task.status, "result": task.result}
```

### Issue: Import errors after adding new package
**Solution**: Install in virtual environment
```bash
source venv/bin/activate
pip install <package>
pip freeze > requirements.txt
```

---

## Quick Start Checklist

Before starting work:

- [ ] On branch `bo_fix_v2`
- [ ] Virtual environment activated
- [ ] Read PLAN.md for context
- [ ] Read current task in INSTRUCTIONS.md
- [ ] Understand what files to modify

---

## Questions?

Write in COMMS.md with `[DEV]` tag. PM will respond.

---

**Good luck! Start with Task 1.1 in INSTRUCTIONS.md**
