# Breakout Screener - V1/V2 Merge Plan

**Project Manager**: Claude (PM)
**Created**: 2024-12-22
**Branch**: bo_fix_v2
**Status**: PLANNING

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

### Phase 3: Code Structure Improvements (Priority: MEDIUM)

**Goal**: Improve maintainability without over-engineering

| Task | Description | Effort |
|------|-------------|--------|
| 3.1 | Add enum types for indicators | 1 hour |
| 3.2 | Add structured logging | 1 hour |
| 3.3 | Reorganize into backend/ folder structure | 2 hours |
| 3.4 | Add Pydantic settings for config | 1 hour |

**Success Criteria**:
- No magic strings for indicators
- JSON-formatted logs
- Clean folder structure

---

### Phase 4: Frontend Enhancements (Priority: LOW)

**Goal**: Improve user experience

| Task | Description | Effort |
|------|-------------|--------|
| 4.1 | Color-code breakout indicators | 30 min |
| 4.2 | Add button loading states | 1 hour |
| 4.3 | Add table filtering/sorting | 4 hours |
| 4.4 | Add CSV export | 2 hours |

**Success Criteria**:
- Visual indicator colors (green/red)
- Loading spinners on buttons
- Filterable/sortable table
- Working CSV download

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

## Approval

- [ ] Plan reviewed by stakeholder
- [ ] Developer acknowledges instructions
- [ ] Ready to begin Phase 1
