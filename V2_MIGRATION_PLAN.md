# Breakout Screener V2 Migration Plan

## Project Overview

**V1 Project**: `/home/anirban/workspace/projects/breakout-screener` (current)  
**V2 Project**: `/home/anirban/workspace/projects/breakout_screener_v2` (new)

**Migration Strategy**: Clean slate approach with selective code reuse from V1  
**Timeline**: 8-12 weeks (5 phases)  
**Approach**: Parallel development - V1 continues running while V2 is built

## Current Todo Status

### High Priority
- [x] Create comprehensive planning document with migration phases
- [x] Generate complete V2 project structure creation script
- [ ] Setup backend with pyproject.toml and modern Python packaging
- [ ] Initialize Next.js 15 frontend with TypeScript and shadcn/ui
- [ ] Configure Docker and docker-compose for development

### Medium Priority
- [ ] Implement configuration management with environment separation
- [ ] Setup structured logging and database configuration
- [ ] Create basic FastAPI app with health checks

### Low Priority
- [ ] Setup development tooling and quality gates

## Phase-by-Phase Migration Plan

### **Phase 1: Foundation Setup (Week 1-2)** ⭐ CURRENT PHASE

#### Week 1: Project Initialization
**Objectives**: Create solid foundation with modern tooling

**Tasks**:
- [x] ~~Analyze V1 codebase structure and identify issues~~
- [x] ~~Design V2 architecture and folder structure~~
- [x] **Create V2 project directory structure**
- [ ] **Setup Python packaging with pyproject.toml**
- [ ] **Initialize Next.js 15 with TypeScript and shadcn/ui**
- [ ] **Configure Docker and docker-compose**
- [ ] **Setup development environment with proper tooling**

**Key V1 References for Reuse**:
- Database schema from `/app/models/breakout_data.py`
- NSE URL configurations from `/app/config.py:22-26`
- API endpoint patterns from `/app/routers/routes.py`
- Business logic from `/app/services/` (needs refactoring)

**Deliverables**:
- [ ] Complete project structure following modern best practices
- [ ] Working development environment with Docker
- [ ] Basic project configuration files
- [ ] Development tooling setup

#### Week 2: Core Infrastructure
**Objectives**: Implement configuration, logging, and database setup

**Tasks**:
- [ ] **Implement configuration management with environment separation**
- [ ] **Setup structured logging with proper log rotation**
- [ ] **Configure database with SQLAlchemy 2.0 and async support**
- [ ] **Setup Redis with connection pooling**
- [ ] **Implement comprehensive error handling framework**

**Key V1 References**:
- Environment variables from V1 `.env` structure
- Database models from `/app/models/`
- Configuration patterns from `/app/config.py`

**Deliverables**:
- [ ] Environment-specific configuration system
- [ ] Structured logging framework
- [ ] Async database setup with proper connection pooling
- [ ] Error handling and exception hierarchy

### **Phase 2: Data Layer Migration (Week 3-4)**

#### Week 3: Database Design
**V1 References to Migrate**:
- `/app/models/breakout_data.py` - Main data model
- `/app/models/master_data.py` - Master table structure
- Database schema from README.md lines 144-217

**Improvements Over V1**:
- Add proper constraints and foreign keys
- Implement proper indexing strategy
- Add audit fields (created_by, updated_by)
- Normalize data structure where applicable

#### Week 4: Data Migration
**V1 Data to Migrate**:
- All records from `breakout_data` table
- All records from `master_table`
- Configuration data and settings

### **Phase 3: Backend API Development (Week 5-7)**

#### Week 5: Core Services
**V1 Services to Refactor**:
- `/app/services/fetch_data.py` → Repository + Service pattern
- `/app/services/nse_data.py` → Async NSE data service
- `/app/services/generate_bo_data.py` → Analysis service
- `/app/services/fetch_scripts.py` → Stock data service

#### Week 6: API Endpoints
**V1 Routes to Migrate**:
- `/app/routers/routes.py:26-30` → Health check endpoint
- `/app/routers/routes.py:33-65` → Get data with pagination
- `/app/routers/routes.py:68-85` → Fetch script symbols
- `/app/routers/routes.py:88-110` → Generate breakout data
- `/app/routers/routes.py:113-130` → Clear chart data

#### Week 7: Background Tasks
**V1 Tasks to Refactor**:
- `/app/tasks/__init__.py:12-15` → Fetch script symbols task
- `/app/tasks/__init__.py:18-22` → Generate BO data task
- `/app/tasks/__init__.py:25-28` → Clear chart data task

### **Phase 4: Frontend Development (Week 8-10)**

#### Week 8: Core Components
**V1 Components to Migrate**:
- `/frontend/src/components/Header/` → Modern header component
- `/frontend/src/components/DataTable/` → Advanced data table
- `/frontend/src/components/InputForm/` → Form with validation
- `/frontend/src/components/Pagination/` → Enhanced pagination

#### Week 9: Features Migration
**V1 Features to Enhance**:
- Data fetching patterns from `/frontend/src/services/api.ts`
- State management improvements over basic useState
- Better error handling and loading states

#### Week 10: UX Improvements
**New Features Not in V1**:
- Real-time updates with WebSockets
- Advanced filtering and search
- Offline support
- Mobile responsiveness

### **Phase 5: DevOps and Deployment (Week 11-12)**

#### Week 11: Infrastructure
- Setup CI/CD pipeline
- Configure monitoring and alerting
- Implement error tracking

#### Week 12: Go-Live
- Performance testing
- Security audit
- Production deployment
- Migration complete

## Technology Stack Migration

### Backend: V1 → V2

| Component | V1 | V2 | Reason for Change |
|-----------|----|----|-------------------|
| Web Framework | FastAPI (basic) | FastAPI (advanced) | Better async support, dependency injection |
| Database ORM | SQLAlchemy 1.x | SQLAlchemy 2.0 | Async support, better performance |
| HTTP Client | requests/selenium | httpx | Async support, better performance |
| Task Queue | Celery (basic) | Celery (advanced) | Better monitoring, error handling |
| Logging | Basic logging | structlog | Structured logging, better debugging |
| Configuration | python-dotenv | pydantic-settings | Type safety, validation |

### Frontend: V1 → V2

| Component | V1 | V2 | Reason for Change |
|-----------|----|----|-------------------|
| React Version | React 19 | React 19 | Keep current version |
| Next.js | Next.js 15 | Next.js 15 (optimized) | Better app router usage |
| State Management | Basic useState | Zustand + TanStack Query | Better data management |
| UI Library | Material-UI | shadcn/ui | More modern, customizable |
| Form Handling | Basic forms | react-hook-form + zod | Better validation, performance |
| Testing | None | Vitest + Testing Library | Comprehensive testing |

## V1 Code Reuse Strategy

### High Priority for Reuse (with refactoring):
1. **Business Logic**: `/app/services/` - Core breakout analysis algorithms
2. **Database Models**: `/app/models/` - Data structure definitions  
3. **API Patterns**: `/app/routers/routes.py` - Endpoint structure
4. **Configuration**: `/app/config.py` - NSE URLs and settings

### Medium Priority for Reuse:
1. **Utility Functions**: `/app/utils/helpers.py` - Date validation, etc.
2. **Frontend Components**: Basic component structure from `/frontend/src/components/`
3. **API Service**: `/frontend/src/services/api.ts` - HTTP client patterns

### Low Priority/Replace:
1. **Error Handling**: `/app/utils/exception_handlers.py` - Replace with better patterns
2. **Database Session**: `/app/db/session.py` - Replace with async version
3. **Celery Setup**: `/app/celery/` - Rewrite with better configuration

## Key Improvement Areas

### 1. Project Structure
**V1 Issues**: Mixed backend folders, scattered configs, logs in source
**V2 Solution**: Clean separation, dedicated config/logs directories

### 2. Error Handling
**V1 Issues**: Generic exception catching, inconsistent patterns
**V2 Solution**: Specific exception hierarchy, structured error responses

### 3. Configuration Management
**V1 Issues**: Single .env file, no environment separation
**V2 Solution**: Environment-specific configs with validation

### 4. Testing
**V1 Issues**: Minimal tests, no frontend testing
**V2 Solution**: Comprehensive test suite with high coverage

### 5. Documentation
**V1 Issues**: Basic setup docs, no API documentation
**V2 Solution**: Complete docs including API specs and architecture

## Migration Checklist

### Pre-Migration
- [ ] Backup V1 database and configurations
- [ ] Document current V1 API endpoints and behavior
- [ ] Identify critical V1 business logic to preserve
- [ ] Setup V2 development environment

### During Migration
- [ ] Maintain V1 operational during V2 development
- [ ] Regular data synchronization between V1 and V2
- [ ] Progressive testing with V1 data in V2 environment
- [ ] User acceptance testing with V2

### Post-Migration
- [ ] Gradual traffic shifting from V1 to V2
- [ ] Performance monitoring and optimization
- [ ] V1 system decommissioning
- [ ] Documentation and knowledge transfer

## Risk Mitigation

### Technical Risks
- **Data Loss**: Comprehensive backup and rollback procedures
- **Performance Issues**: Load testing with production data
- **Integration Problems**: Extensive integration testing

### Business Risks
- **Downtime**: Blue-green deployment strategy
- **User Disruption**: Gradual migration with fallback options
- **Feature Parity**: Comprehensive feature comparison and testing

## Success Metrics

### Technical Metrics
- [ ] 100% feature parity with V1
- [ ] <2s API response times (improvement from V1)
- [ ] 99.9% uptime during migration
- [ ] >90% test coverage

### Business Metrics
- [ ] Zero data loss during migration
- [ ] <1 hour total downtime
- [ ] User satisfaction maintained or improved
- [ ] All V1 functionality preserved

---

**Next Action**: Execute the V2 project structure creation script and begin Phase 1 implementation.