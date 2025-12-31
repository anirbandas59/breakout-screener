# Breakout Screener - V1/V2 Merge Plan

**Project Manager**: Claude (PM)
**Created**: 2024-12-22
**Updated**: 2025-12-31
**Branch**: bo_fix_v2
**Status**: PHASE 1 & 2 COMPLETE - READY FOR PHASE 3

---

## Executive Summary

This plan merges the best aspects of V1 (working code, simplicity) with V2 (architecture, type safety) to create a production-ready Breakout Screener that can process 400-500 NSE stocks efficiently.

---

## Goals

1. **Primary**: Enable processing of 400-500 scripts in ~10 minutes (currently 5 scripts in ~1.5 min)
2. **Secondary**: Improve code structure without over-engineering
3. **Tertiary**: Add user feedback (progress tracking, notifications)

---

## What We're Taking From Each Branch

### From V2 (Architecture & Patterns)

| Item | Benefit |
|------|---------|
| Project structure (`backend/`, `frontend/`) | Clean organization |
| Pydantic schemas for request validation | Type safety, auto-docs |
| Enum types for indicators | No magic strings |
| Structured logging (structlog) | Better debugging |
| Docker setup (optional) | Easy deployment |
| TanStack Query (frontend) | Better state management |

### From V1 (Working Implementation)

| Item | Benefit |
|------|---------|
| Working Celery task integration | Proven async processing |
| Focused API endpoints (~10) | No bloat |
| Direct service layer | Simple, traceable |
| IST-aware date logic | Domain-specific |
| Breakout analysis formulas | Tested business logic |
| Database schema (simplified) | Works without UUID complexity |

### New Additions

| Item | Benefit |
|------|---------|
| yfinance for price data | 20x faster than Selenium |
| Progress tracking in tasks | User feedback |
| Celery task timeout config | Prevent zombie tasks |
| Toast notifications (frontend) | User feedback |
| Retry logic (tenacity) | Resilience |

---

## Architecture Overview

```
breakout-screener/
├── backend/                      # FastAPI application
│   ├── app/
│   │   ├── main.py               # Entry point (from V1)
│   │   ├── config.py             # Pydantic settings (V2 style)
│   │   ├── models/               # SQLAlchemy models (V1 simplified)
│   │   ├── schemas/              # Pydantic schemas (from V2)
│   │   ├── services/             # Business logic (V1 + yfinance)
│   │   ├── routers/              # API endpoints (V1 focused)
│   │   ├── tasks/                # Celery tasks (V1 + progress)
│   │   └── utils/                # Helpers (V1)
│   ├── requirements.txt
│   └── Dockerfile (optional)
│
├── frontend/                     # Next.js application
│   ├── src/
│   │   ├── app/                  # Pages (V1 structure)
│   │   ├── components/           # Components (V1 + improvements)
│   │   ├── services/             # API calls (V1)
│   │   ├── hooks/                # TanStack Query hooks (from V2)
│   │   └── types/                # TypeScript types (enhanced)
│   └── package.json
│
├── Planning/                     # This folder
├── docs/                         # Documentation
└── docker-compose.yml (optional)
```

---

## Implementation Phases

### Phase 1: Critical Backend Fixes (Priority: HIGHEST)

**Goal**: Enable 500 script processing in ~10 minutes

| Task | Description | Effort |
|------|-------------|--------|
| 1.1 | Replace Selenium with yfinance for price data | 2 hours |
| 1.2 | Remove 5-script limit in generate_bo_data.py | 5 min |
| 1.3 | Add Celery task timeout configuration | 15 min |
| 1.4 | Add progress tracking to generate_bo_data | 30 min |
| 1.5 | Add retry logic for failed scripts | 1 hour |

**Success Criteria**:
- 500 scripts processed without errors
- Runtime < 15 minutes
- Progress visible in task status

---

### Phase 2: Connect Missing Features (Priority: HIGH)

**Goal**: Make all UI controls functional

| Task | Description | Effort |
|------|-------------|--------|
| 2.1 | Connect "Start From" field to backend | 2 hours |
| 2.2 | Add Pydantic schemas for request validation | 1 hour |
| 2.3 | Update frontend to show progress | 1 hour |
| 2.4 | Add toast notifications | 1 hour |

**Success Criteria**:
- "Start From" resumes from specified index
- Progress bar shows X of Y scripts
- Success/error toasts displayed

---

### Phase 3: Code Structure Improvements (Priority: MEDIUM - OPTIONAL)

**Goal**: Improve maintainability without over-engineering

**Status**: Not Started (Optional - only proceed if requested by stakeholder)

**Context**: Phase 1 & 2 delivered a production-ready application. Phase 3 focuses on code quality improvements that make the codebase easier to maintain and extend, but are not critical for functionality.

| Task | Description | Effort | Benefit |
|------|-------------|--------|---------|
| 3.1 | Add enum types for indicators | 1 hour | Type safety, no magic strings |
| 3.2 | Refactor CPR calculation into separate module | 2 hours | Better testability, reusability |
| 3.3 | Add input validation with Pydantic for all models | 2 hours | Catch errors early, auto-docs |
| 3.4 | Add comprehensive error handling | 2 hours | Better debugging, user feedback |
| 3.5 | Add API response schemas | 1 hour | Consistent responses, type safety |

**Success Criteria**:
- No magic strings for indicators (use enums)
- Input validation on all endpoints
- Consistent error response format
- CPR logic isolated and testable
- All API responses follow schema

**Files to Modify**:
- `app/models/enums.py` (new) - Indicator enums
- `app/models/schemas.py` (new) - Response schemas
- `app/services/cpr_calculator.py` (new) - Extracted CPR logic
- `app/services/generate_bo_data.py` - Use enums, extracted CPR
- `app/routers/routes.py` - Add response schemas
- `app/utils/error_handlers.py` (new) - Centralized error handling

**What NOT to Do** (Avoid Over-Engineering):
- Don't add unnecessary abstraction layers
- Don't reorganize folder structure (current structure works)
- Don't add complex design patterns (keep it simple)
- Don't add logging libraries (basic logging is sufficient)
- Don't add Docker/deployment configs (out of scope)

---

### Phase 4: Frontend Enhancements (Priority: LOW - OPTIONAL)

**Goal**: Improve user experience and data visualization

**Status**: Not Started (Optional - only proceed if requested by stakeholder)

**Context**: Phase 1 & 2 delivered a functional UI with progress tracking and notifications. Phase 4 focuses on polish and advanced features that improve usability but are not critical.

| Task | Description | Effort | Benefit |
|------|-------------|--------|---------|
| 4.1 | Color-code breakout indicators | 1 hour | Visual clarity (green/red/yellow) |
| 4.2 | Add button loading states | 1 hour | Better UX during async operations |
| 4.3 | Add table filtering/sorting | 4 hours | Find stocks faster |
| 4.4 | Add CSV export | 2 hours | Export data for Excel analysis |
| 4.5 | Add date range picker | 2 hours | View historical analysis |
| 4.6 | Add column visibility toggle | 2 hours | Customize table view |
| 4.7 | Add dark mode toggle | 3 hours | User preference (already supported) |
| 4.8 | Add keyboard shortcuts | 2 hours | Power user efficiency |

**Success Criteria**:
- Indicator colors: GREEN (bullish), RED (bearish), YELLOW (neutral)
- Loading spinners on all async buttons
- Table sortable by any column
- Table filterable by script name, indicators
- CSV export includes all visible data
- Date range picker shows data for selected period
- Column visibility persisted in localStorage
- Keyboard shortcuts documented in UI

**Files to Modify**:
- `frontend/src/components/DataTable/DataTable.tsx` - Add sorting, filtering, colors
- `frontend/src/components/DataTable/ColumnToggle.tsx` (new) - Column visibility
- `frontend/src/components/DataTable/ExportButton.tsx` (new) - CSV export
- `frontend/src/components/InputForm/InputForm.tsx` - Add loading states
- `frontend/src/components/DateRangePicker/DateRangePicker.tsx` (new) - Date selection
- `frontend/src/components/KeyboardShortcuts/KeyboardShortcuts.tsx` (new) - Shortcuts help
- `frontend/src/hooks/useKeyboardShortcuts.ts` (new) - Shortcut logic
- `frontend/src/utils/csvExport.ts` (new) - CSV generation logic
- `frontend/src/styles/indicators.css` (new) - Indicator color styles

**Dependencies to Add**:
- `react-table` or `@tanstack/react-table` - Table sorting/filtering
- `papaparse` - CSV export
- `react-datepicker` - Date range picker

**What NOT to Do** (Keep It Simple):
- Don't add complex charting libraries (not required)
- Don't add WebSocket for real-time updates (polling works)
- Don't add user authentication (out of scope)
- Don't add multi-language support (not required)
- Don't redesign entire UI (current design works)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| yfinance rate limiting | Medium | High | Add delays, retry logic |
| Breaking existing functionality | Low | High | Test each change incrementally |
| Scope creep | High | Medium | Strict phase boundaries |
| Database migration issues | Low | Medium | No schema changes in Phase 1-2 |

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Scripts processed | 5 | 500 |
| Processing time | ~1.5 min (5 scripts) | ~10 min (500 scripts) |
| User feedback | None | Progress bar + toasts |
| Error recovery | None | Retry + resume capability |

---

## Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1 | 1 day | None |
| Phase 2 | 1 day | Phase 1 |
| Phase 3 | 1 day | Phase 2 |
| Phase 4 | 2 days | Phase 3 |

**Total Estimated**: 5-6 days

---

## Review Points

After each phase:
1. Developer updates checklist in INSTRUCTIONS.md
2. Developer writes status in COMMS.md
3. PM reviews implemented code
4. PM verifies checklist items
5. PM approves or requests changes

---

## Files in This Folder

| File | Purpose |
|------|---------|
| PLAN.md | This file - overall strategy |
| INSTRUCTIONS.md | Detailed tasks with checklist |
| COMMS.md | Communication between PM and Developer |
| DEVELOPER_INSTRUCTIONS.md | Workflow guide for developer |

---

## Project Status (Updated 2025-12-31)

### Completed Phases

**Phase 1: Critical Backend Fixes** ✅ COMPLETE
- Status: 100% (375/375 points)
- Completion Date: 2025-12-31
- All 5 tasks completed and verified
- All 4 completion tests passed
- Performance: 60x improvement (0.15s vs 20s per stock)
- Processing capacity: 500 scripts in ~10-15 minutes

**Phase 2: Connect Missing Features** ✅ COMPLETE
- Status: 100% (300/300 points)
- Completion Date: 2025-12-30
- All 4 tasks completed and verified (including Task 2.0 Database Setup)
- Start From field fully functional
- Toast notifications operational
- Real-time progress tracking working

**Additional Work Completed**:
- Tailwind CSS v4 migration (75/75 points)
- Database setup and verification
- Phase 1 completion testing (all 4 tests passed)

### Next Steps

**Phase 3: Code Structure Improvements** - OPTIONAL
- Status: Not Started
- Priority: MEDIUM
- Estimated Duration: 1-2 days
- Focus: Maintainability without over-engineering

**Phase 4: Frontend Enhancements** - OPTIONAL
- Status: Not Started
- Priority: LOW
- Estimated Duration: 2-3 days
- Focus: User experience improvements

## Approval

- [✓] Phase 1 reviewed and approved by PM - 2025-12-31
- [✓] Phase 2 reviewed and approved by PM - 2025-12-30
- [✓] Production ready - all critical features operational
- [ ] Phase 3 approval (if stakeholder requests)
- [ ] Phase 4 approval (if stakeholder requests)
