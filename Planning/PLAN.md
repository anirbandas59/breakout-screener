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

### Phase 4: Frontend Enhancements (Priority: MEDIUM - Part of Complete Redesign)

**Goal**: Enhance current UI with advanced table features and improved UX

**Status**: Part of Phase 5 comprehensive redesign

**Context**: Phase 4 tasks are incorporated into the complete UI redesign (Phase 5). These enhancements will be implemented using shadcn/ui components and TanStack Table during the redesign.

| Task | Description | Implementation in Phase 5 |
|------|-------------|---------------------------|
| 4.1 | Color-code breakout indicators | Phase 5 - Custom badge components with color variants |
| 4.2 | Add button loading states | Phase 5 - shadcn Button with loading prop |
| 4.3 | Add table filtering/sorting | Phase 5 - TanStack Table with full sort/filter |
| 4.4 | Add CSV export | Phase 5 - papaparse integration in Reports page |
| 4.5 | Add date range picker | Phase 5 - shadcn Calendar for Reports page |
| 4.6 | Add column visibility toggle | Phase 5 - TanStack Table column visibility |
| 4.7 | Add dark mode toggle | Phase 5 - next-themes with toggle in Header |
| 4.8 | Add keyboard shortcuts | Phase 5 - Custom hook for shortcuts |

**Note**: All Phase 4 features will be implemented as part of the comprehensive UI redesign (Phase 5) rather than as standalone enhancements. This provides better integration, consistent design system, and avoids duplicate work.

---

### Phase 5: Complete UI Redesign (Priority: HIGH - Comprehensive Transformation)

**Goal**: Transform Breakout Screener into a modern, multi-page dashboard with comprehensive design system, advanced features, and complete dark mode

**Status**: Planned - Ready for implementation

**Timeline**: 3-4 weeks (20 days)

**Approach**: Incremental migration with rollback points after each sub-phase

---

#### 5.0 Overview & Strategy

**Current State**:
- Single-page application (only `/` route exists)
- 9 components using local state with props drilling
- 95% Tailwind utilities, 5% MUI (Divider + 3 icons)
- Incomplete dark mode (only 23 `dark:` classes)
- Basic 19-column table with no sort/filter/search
- Bundle includes unused MUI (~500KB total)

**Target State**:
- Multi-page dashboard with sidebar navigation (Scanner/Reports/Settings/About)
- shadcn/ui design system with consistent components
- Jotai state management (eliminate props drilling)
- TanStack Table with advanced features
- Complete dark mode with theme toggle
- Optimized bundle size (~120KB - removing MUI)

**Key Design Decisions**:
1. **Framework**: shadcn/ui + Tailwind CSS v4 (keep existing Tailwind, add shadcn)
2. **State**: Jotai (already installed, atomic state management)
3. **Table**: TanStack Table (industry standard, excellent TypeScript support)
4. **Theme**: next-themes (class-based dark mode)
5. **Icons**: lucide-react (replace MUI icons)

---

#### 5.1 Phase 1: Foundation & Infrastructure (Days 1-2)

**Goal**: Set up shadcn/ui, establish design system, create multi-page routing

**Tasks**:

**5.1.1 Install shadcn/ui**
```bash
npx shadcn@latest init
npm install class-variance-authority clsx tailwind-merge lucide-react next-themes
npx shadcn@latest add button card input label separator dialog dropdown-menu switch toast skeleton
```

**5.1.2 Update Design System**
- File: `frontend/src/app/globals.css`
- Replace `@theme` block with shadcn CSS variables (HSL color system)
- Add dark mode using `class` strategy
- Keep existing font variables (Inter, Playfair Display)

**5.1.3 Create Utility Helper**
- File: `frontend/src/lib/utils.ts`
- Create `cn()` helper for merging Tailwind classes

**5.1.4 Create Multi-Page Routing**
```
frontend/src/app/
├── (dashboard)/              # Route group with shared layout
│   ├── layout.tsx           # Sidebar + header layout
│   ├── page.tsx             # Scanner (current HomePage)
│   ├── reports/page.tsx     # Historical reports
│   ├── settings/page.tsx    # App settings + theme
│   └── about/page.tsx       # Documentation
```

**Routes**:
- `/` → Scanner interface
- `/reports` → Historical data view
- `/settings` → Settings + theme toggle
- `/about` → App info

**5.1.5 Create Theme Provider**
- File: `frontend/src/components/theme-provider.tsx`
- Wrap app with next-themes provider
- Update: `frontend/src/app/layout.tsx`

**Deliverables**:
- shadcn/ui configured and working
- Multi-page routing structure created
- Theme provider integrated
- Design system CSS variables defined

---

#### 5.2 Phase 2: State Management & Layout (Days 3-5)

**Goal**: Implement Jotai state atoms, create dashboard layout, migrate Header/Navbar

**Tasks**:

**5.2.1 Create Jotai Store**
- File: `frontend/src/store/atoms.ts`
- Define atoms for scanner state, table state, UI state
- Eliminates props drilling from HomePage

**Atoms**:
```typescript
// Scanner state
dateAtom, taskIdAtom, scriptsAnalyzedAtom, startRefreshAtom,
progressAtom, startTimeAtom, runningTimeAtom, scriptFetchedOnAtom

// Table state
tableDataAtom, tablePageAtom, tableLimitAtom, totalPagesAtom, isLoadingAtom

// UI state
sidebarCollapsedAtom
```

**5.2.2 Create Dashboard Layout**
- File: `frontend/src/app/(dashboard)/layout.tsx`
- Flexbox layout: Sidebar + (Header + Main content)
- Responsive: Sidebar becomes drawer on mobile

**5.2.3 Create Sidebar Component**
- File: `frontend/src/components/layouts/Sidebar.tsx`
- Navigation items: Scanner, Reports, Settings, About
- Active link highlighting using `usePathname()`
- Icons from lucide-react
- Collapsible state from Jotai

**5.2.4 Update Header Component**
- File: `frontend/src/components/Header/Header.tsx`
- Remove embedded Navbar (moved to Sidebar)
- Add theme toggle button (moon/sun icon)
- Add hamburger menu for mobile
- Use shadcn Button components

**5.2.5 Delete Old Navbar**
- File: `frontend/src/components/Navbar/Navbar.tsx` (DELETE)
- Functionality moved to Sidebar

**Deliverables**:
- Jotai atoms defined and working
- Dashboard layout with sidebar navigation
- Theme toggle in header
- No more props drilling

---

#### 5.3 Phase 3: Component Migration (Days 6-8)

**Goal**: Replace MUI components, migrate to shadcn/ui, update for dark mode

**Tasks**:

**5.3.1 Replace Toast System**
```bash
npm uninstall react-hot-toast
npx shadcn@latest add toast
```
- Update all API calls to use new toast syntax
- Files: `api.ts`, `InputForm.tsx`, `HomePage.tsx`

**5.3.2 Migrate InputForm**
- File: `frontend/src/components/InputForm/InputForm.tsx`
- Replace MUI `<Divider>` with shadcn `<Separator>`
- Replace native inputs with shadcn `<Input>` + `<Label>`
- Remove local state → use Jotai atoms
- Wrap in shadcn `<Card>` component
- Full dark mode support

**5.3.3 Migrate ButtonGroups**
- File: `frontend/src/components/ButtonGroups/ButtonGroups.tsx`
- Replace custom styles with shadcn `<Button>` variants
- Use semantic colors: `variant="default|destructive|outline"`
- Add loading states with lucide-react icons
- Remove props → use Jotai atoms

**5.3.4 Migrate DisplayFields**
- File: `frontend/src/components/DisplayFields/DisplayFields.tsx`
- Wrap in shadcn `<Card>`
- Remove hardcoded yellow background → use `bg-card`
- Read state from Jotai atoms
- Full dark mode

**5.3.5 Migrate Pagination**
```bash
npx shadcn@latest add select
```
- File: `frontend/src/components/Pagination/Pagination.tsx`
- Replace MUI icons with lucide-react icons
- Use shadcn `<Button>` and `<Select>`
- Remove props → use Jotai atoms

**5.3.6 Migrate Loader**
- File: `frontend/src/components/Loader/Loader.tsx`
- Replace custom spinner with shadcn `<Skeleton>`

**Deliverables**:
- All components using shadcn/ui
- No MUI dependencies in code (ready for removal)
- Full dark mode support on all components
- State managed via Jotai atoms

---

#### 5.4 Phase 4: Advanced Table Implementation (Days 9-13)

**Goal**: Replace basic table with TanStack Table + advanced features

**Tasks**:

**5.4.1 Install Dependencies**
```bash
npm install @tanstack/react-table
npx shadcn@latest add table popover checkbox badge
```

**5.4.2 Create Column Definitions**
- File: `frontend/src/components/DataTable/columns.tsx`
- Sortable columns
- Custom cell renderers (color-coded badges for indicators)
- Numeric formatting for OHLCV data
- Action column with "View Chart" link

**5.4.3 Create Custom Cells**
- File: `frontend/src/components/DataTable/cells.tsx`
- `IndicatorBadge` - Color-coded badges (green/red/yellow)
- `NumericCell` - Right-aligned formatted numbers
- `ViewChartLink` - External link with icon

**5.4.4 Create Table Toolbar**
- File: `frontend/src/components/DataTable/DataTableToolbar.tsx`
- Global search input (with debounce using existing `use-debounce`)
- Column visibility dropdown
- Active filter chips
- Reset filters button

**5.4.5 Rewrite DataTable**
- File: `frontend/src/components/DataTable/DataTable.tsx`
- Complete rewrite using TanStack Table
- Multi-column sorting
- Global search + column filters
- Column visibility toggle
- Responsive horizontal scroll
- Sticky header

**Features**:
```typescript
const table = useReactTable({
  data: tableData,
  columns,
  state: { sorting, columnFilters, columnVisibility, globalFilter },
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
})
```

**5.4.6 Simplify HomePage**
- File: `frontend/src/components/HomePage/HomePage.tsx`
- Remove all state management (moved to Jotai)
- Simplify to layout component

**Deliverables**:
- TanStack Table fully functional
- Sorting, filtering, search working
- Column visibility toggle
- Color-coded indicator badges
- Simplified HomePage component

---

#### 5.5 Phase 5: New Pages & Final Polish (Days 14-20)

**Goal**: Implement new pages, complete dark mode, add accessibility

**Tasks**:

**5.5.1 Create Reports Page**
```bash
npx shadcn@latest add calendar
```
- File: `frontend/src/app/(dashboard)/reports/page.tsx`
- Date range picker
- Summary statistics cards (Total Scripts, Success Rate, Breakout Count)
- Historical data table (reuse DataTable component)
- Export to CSV functionality

**5.5.2 Create Settings Page**
```bash
npx shadcn@latest add radio-group alert-dialog
```
- File: `frontend/src/app/(dashboard)/settings/page.tsx`
- **Appearance**: Theme toggle (Light/Dark/System), sidebar settings
- **Scanner Settings**: Default pivot gap, rows per page, auto-refresh
- **Data Management**: Clear cache, clear all data (with confirmation dialog)

**5.5.3 Create About Page**
- File: `frontend/src/app/(dashboard)/about/page.tsx`
- App description
- Technical indicators explanation (CPR, breakout, volume)
- Version info
- Credits/documentation links

**5.5.4 Dark Mode Completion Pass**

Audit all components for 100% dark mode coverage:
- [ ] All Cards use `bg-card`
- [ ] All text uses `text-foreground` or `text-muted-foreground`
- [ ] All borders use `border-border`
- [ ] All inputs use proper background with contrast
- [ ] Table rows use `bg-muted/50` for alternating colors
- [ ] Buttons use proper variant colors
- [ ] Progress bar uses theme colors

**5.5.5 Accessibility Improvements**

**ARIA Labels**:
- All buttons have `aria-label` or visible text
- Form inputs have associated `<Label>` components
- Table has proper `role` attributes
- Dialogs have focus trap

**Keyboard Navigation**:
- All interactive elements keyboard accessible
- Table supports arrow key navigation
- Sidebar toggleable with keyboard
- Form submission with Enter key

**Screen Reader Support**:
- Semantic HTML (`<nav>`, `<main>`, `<header>`)
- `aria-live` regions for progress updates
- `aria-current="page"` for active nav link

**5.5.6 Remove MUI Dependencies**
```bash
npm uninstall @mui/material @mui/icons-material @emotion/react @emotion/styled
```

Verify no imports remain:
```bash
grep -r "@mui" frontend/src/
grep -r "@emotion" frontend/src/
```

**Bundle Size Impact**: ~500KB → ~120KB (380KB savings)

**5.5.7 Performance Optimization**
1. Code splitting - Dynamic imports for heavy components
2. Memoization - `useMemo` for column definitions
3. Debouncing - Use `use-debounce` for search
4. Virtual scrolling - Consider for tables with >100 rows

**Deliverables**:
- All pages implemented and functional
- 100% dark mode coverage
- WCAG 2.1 AA compliance
- MUI removed, bundle optimized
- Performance targets met

---

#### 5.6 Dependencies Summary

**To Add**:
```json
{
  "class-variance-authority": "^0.7.1",
  "clsx": "^2.1.1",
  "tailwind-merge": "^2.5.5",
  "lucide-react": "^0.469.0",
  "next-themes": "^0.4.4",
  "@tanstack/react-table": "^8.20.6",
  "@radix-ui/react-*": "Multiple packages (installed by shadcn CLI)",
  "papaparse": "^5.4.1"
}
```

**To Remove**:
```json
{
  "@mui/material": "^7.3.6",
  "@mui/icons-material": "^7.3.6",
  "@emotion/react": "^11.14.0",
  "@emotion/styled": "^11.14.1",
  "react-hot-toast": "^2.6.0"
}
```

**To Keep**:
```json
{
  "axios": "^1.13.2",
  "jotai": "^2.16.1",
  "use-debounce": "^10.0.4"
}
```

---

#### 5.7 File Changes Summary

**New Files (19)**:
- `frontend/src/lib/utils.ts`
- `frontend/src/components/theme-provider.tsx`
- `frontend/src/store/atoms.ts`
- `frontend/src/app/(dashboard)/layout.tsx`
- `frontend/src/app/(dashboard)/reports/page.tsx`
- `frontend/src/app/(dashboard)/settings/page.tsx`
- `frontend/src/app/(dashboard)/about/page.tsx`
- `frontend/src/components/layouts/Sidebar.tsx`
- `frontend/src/components/layouts/ThemeToggle.tsx`
- `frontend/src/components/DataTable/columns.tsx`
- `frontend/src/components/DataTable/cells.tsx`
- `frontend/src/components/DataTable/DataTableToolbar.tsx`
- `frontend/src/components/ui/*` (shadcn components - auto-generated)
- `frontend/src/utils/csvExport.ts`

**Updated Files (11)**:
- `frontend/src/app/globals.css`
- `frontend/src/app/layout.tsx`
- `frontend/src/app/page.tsx` (move to (dashboard)/page.tsx)
- `frontend/src/components/Header/Header.tsx`
- `frontend/src/components/InputForm/InputForm.tsx`
- `frontend/src/components/ButtonGroups/ButtonGroups.tsx`
- `frontend/src/components/DisplayFields/DisplayFields.tsx`
- `frontend/src/components/Pagination/Pagination.tsx`
- `frontend/src/components/Loader/Loader.tsx`
- `frontend/src/components/HomePage/HomePage.tsx`
- `frontend/src/components/DataTable/DataTable.tsx`
- `frontend/src/services/api.ts`

**Deleted Files (1)**:
- `frontend/src/components/Navbar/Navbar.tsx`

---

#### 5.8 Testing Strategy

**Per-Phase Testing**:
1. Visual regression (before/after screenshots)
2. Functional testing (all API calls work)
3. Theme testing (toggle light/dark on every page)
4. Responsive testing (mobile/tablet/desktop)
5. Accessibility testing (axe DevTools)

**Critical Paths**:
- [ ] Fetch stock list → view in table
- [ ] Generate breakout data → progress → refresh table
- [ ] Sort/filter/search table
- [ ] Clear data operations
- [ ] Theme persistence across refreshes
- [ ] Navigation between pages

**Rollback Strategy**:
- After each sub-phase: Commit with descriptive message
- Tag releases: `v2.0.0-phase5.1`, `v2.0.0-phase5.2`, etc.
- Create backup branches
- If issues occur: Revert to previous tag, fix, re-integrate

---

#### 5.9 Success Metrics

**Performance**:
- [ ] Initial page load < 2s
- [ ] Theme toggle < 100ms
- [ ] Table render (500 rows) < 1s
- [ ] Bundle size < 300KB (gzipped)

**Quality**:
- [ ] 100% dark mode coverage
- [ ] WCAG 2.1 AA compliance
- [ ] Zero console errors/warnings
- [ ] All routes functional

**User Experience**:
- [ ] Mobile-responsive (320px to 4K)
- [ ] Keyboard navigation works
- [ ] Theme persists across sessions
- [ ] Table filters/sorts correctly

---

#### 5.10 Risk Mitigation

**Potential Issues**:

1. **API Compatibility**
   - Risk: Toast changes break API error handling
   - Mitigation: Update all API calls in Phase 5.3

2. **State Management Migration**
   - Risk: Jotai atoms not syncing correctly
   - Mitigation: Test each atom individually, add DevTools

3. **Table Performance**
   - Risk: TanStack Table slow with 500 rows
   - Mitigation: Implement server-side pagination, virtual scrolling

4. **Dark Mode Edge Cases**
   - Risk: Some components not themed correctly
   - Mitigation: Comprehensive checklist in Phase 5.5.4

5. **Bundle Size Increase**
   - Risk: Radix UI adds too much size
   - Mitigation: Tree-shaking verification, code splitting

---

#### 5.11 Implementation Timeline

**Week 1: Foundation + State**
- Days 1-2: Phase 5.1 (shadcn setup, routing, theme)
- Days 3-5: Phase 5.2 (Jotai, layouts, header)

**Week 2: Components + Table Start**
- Days 6-8: Phase 5.3 (Migrate existing components)
- Days 9-10: Phase 5.4 (Start TanStack Table)

**Week 3: Table Finish + Pages**
- Days 11-13: Phase 5.4 (Finish TanStack Table)
- Days 14-15: Phase 5.5 (Start new pages)

**Week 4: Pages + Polish**
- Days 16-17: Phase 5.5 (Finish pages, dark mode)
- Days 18-19: Phase 5.5 (Accessibility, testing)
- Day 20: Phase 5.5 (Remove MUI, final optimization)

---

**What NOT to Do** (Avoid Over-Engineering):
- Don't add complex charting libraries (unless explicitly needed)
- Don't add WebSocket for real-time updates (polling works well)
- Don't add user authentication (out of scope)
- Don't add multi-language support (not required)
- Don't create custom component library (shadcn/ui provides everything)
- Don't add unnecessary animations (keep it performant)

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

**Phase 3: Code Structure Improvements** ✅ COMPLETE
- Status: 100% (125/125 points)
- Completion Date: 2025-12-31
- All 5 tasks completed and verified
- Code quality: Type safety, maintainability, error handling
- Focus: Maintainability without over-engineering

**Phase 4: Frontend Enhancements** - DEFERRED (Part of Phase 5)
- Status: Merged into Phase 5 Complete UI Redesign
- Priority: MEDIUM
- Note: All Phase 4 features will be implemented as part of comprehensive Phase 5 redesign
- See Phase 5 plan for detailed implementation strategy

**Phase 5: Complete UI Redesign** - READY FOR IMPLEMENTATION
- Status: Planned - Ready to start
- Priority: HIGH (User Experience Transformation)
- Estimated Duration: 20 days (3-4 weeks)
- Focus: Multi-page dashboard, shadcn/ui, TanStack Table, dark mode
- Approach: Incremental migration with rollback points

## Approval

- [✓] Phase 1 reviewed and approved by PM - 2025-12-31
- [✓] Phase 2 reviewed and approved by PM - 2025-12-30
- [✓] Phase 3 reviewed and approved by PM - 2025-12-31
- [✓] Production ready - all critical features operational
- [ ] Phase 5 approval - awaiting stakeholder decision to proceed
