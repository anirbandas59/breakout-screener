# V2 Business Logic Implementation Plan

## CRITICAL MISSING COMPONENTS IDENTIFIED

After thorough analysis comparing V1 and V2 codebases, I've identified 5 major missing functionality areas that are essential for the breakout screener's core business operations:

**Phase 1: NSE Data Extraction Service (Week 1)**

Implement Missing: 
- ✅ Selenium web scraping service for 5 NSE indices
- ✅ Chrome WebDriver configuration and utilities  
- ✅ NSE URL management from environment config
- ✅ Chart link generation for GoCharting.com integration
- ✅ Script symbol extraction and normalization

**Phase 2: Historical Data Fetching Service (Week 1)**

Implement Missing:
- ✅ Yahoo Finance integration service
- ✅ Historical OHLCV data retrieval
- ✅ Pandas-based data processing
- ✅ Date range validation and error handling

**Phase 3: Breakout Calculation Engine (Week 2)**

Implement Missing:
- ✅ CPR calculation algorithms: (H+L+C)/3
- ✅ Support/Resistance level calculations  
- ✅ Volume analysis with 10-day averages
- ✅ Narrow gap detection with pivot thresholds
- ✅ Candle pattern analysis (Red/Green/Doji classification)
- ✅ Previous high analysis (10-day maximum)
- ✅ Breakout detection multi-criteria logic

**Phase 4: Celery Task Queue Implementation (Week 2-3)**

## Implement Missing:
- ✅ Celery worker configuration and setup
- ✅ Core task definitions: fetch_symbols, generate_analysis, clear_data  
- ✅ Redis integration for task management
- ✅ Task monitoring and status tracking
- ✅ Error handling and retry mechanisms

**Phase 5: Service Layer & Business Logic (Week 3)**

## Implement Missing:
- ✅ Service layer architecture for business operations
- ✅ Data processing workflows
- ✅ Archive/migration logic for master data
- ✅ Suspension handling for interruptible analysis
- ✅ Integration between services and existing repositories

## DELIVERABLES

- Review current tech stack from V2 and use them for implementation. For example, if a btter tool is available for data extraction instead of selenium.
- Complete NSE data extraction capability
- Yahoo Finance historical data integration  
- Full breakout analysis calculation engine
- Async task processing with Celery/Redis
- Comprehensive service layer with V1 business logic preservation
- End-to-end functional parity with V1 system

## VALIDATION

- All V1 Celery tasks replicated in V2
- Technical analysis formulas exactly preserved
- Multi-NSE index support maintained  
- Data processing workflows functional
- Background task system operational