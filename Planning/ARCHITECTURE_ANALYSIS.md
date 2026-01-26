You are a **principal software architect, backend engineer (Python), frontend engineer (Next.js), performance specialist, and security reviewer**.

Perform a **full-stack analysis of this local project**, covering both the **Python backend** and **Next.js frontend**. Produce a structured, actionable report with **file-level references**.

---

## 1. Code Quality Review

### Python Backend

* Review adherence to **PEP 8**, **PEP 257**, and Pythonic best practices
* Identify code smells such as:

  * God functions / classes
  * Deep nesting and complex conditionals
  * Improper exception handling
  * Mutable default arguments
* Evaluate use of:

  * Type hints and `mypy`-friendliness
  * Dataclasses / Pydantic models
  * Logging vs `print` statements
* Highlight duplicated business logic and poor separation of concerns

### Next.js Frontend

* Review component structure and reusability
* Identify anti-patterns such as:

  * Overloaded components
  * Excessive prop drilling
  * Inline business logic in UI components
* Evaluate:

  * File-based routing structure
  * Usage of Server vs Client Components
  * Custom hooks and shared utilities
* Check readability, naming conventions, and TypeScript usage (if applicable)

---

## 2. Performance Optimization

### Python Backend

* Identify:

  * Inefficient algorithms and unnecessary loops
  * N+1 database query issues
  * Blocking I/O in async contexts
  * Poor caching strategies
* Evaluate:

  * Use of async frameworks (FastAPI / asyncio)
  * Connection pooling and request lifecycle
  * Background task handling
* Recommend optimizations with expected performance gains

### Next.js Frontend

* Analyze:

  * Bundle size and unnecessary imports
  * Over-rendering and missing memoization
  * Inefficient data fetching patterns
* Review:

  * `getServerSideProps`, `getStaticProps`, Server Actions, or App Router usage
  * Image optimization (`next/image`)
  * Font and script loading strategies
* Suggest performance improvements and Core Web Vitals impact

---

## 3. Security Vulnerability Assessment

### Python Backend

* Check for:

  * SQL / NoSQL injection risks
  * Unsafe deserialization
  * Insecure authentication or token handling
  * Secrets hardcoded in code or configs
* Review:

  * Input validation and schema enforcement
  * Error handling and information leakage
  * Rate limiting and abuse protection
* Assign **severity levels** and recommend mitigations

### Next.js Frontend

* Identify:

  * XSS vectors
  * Unsafe use of `dangerouslySetInnerHTML`
  * Exposure of sensitive environment variables
* Review:

  * Client-side authentication logic
  * API route security
  * CSRF protections where applicable

---

## 4. Architecture Assessment

### Backend Architecture

* Evaluate:

  * Layering (API, services, domain, persistence)
  * Business logic placement
  * Coupling between modules
* Assess scalability, testability, and maintainability
* Identify architectural risks and suggest improvements

### Frontend Architecture

* Review:

  * App Router vs Pages Router design
  * State management approach (Context, Zustand, Redux, etc.)
  * API boundary design between frontend and backend
* Comment on long-term maintainability and feature growth

---

## 5. Dependency Analysis

### Python Backend

* List major dependencies and their purpose
* Identify:

  * Unused or redundant packages
  * Outdated or unmaintained libraries
  * Security-sensitive dependencies
* Suggest modern or safer alternatives

### Next.js Frontend

* Review:

  * npm/yarn/pnpm dependencies
  * Duplicate or overlapping libraries
  * Large dependencies affecting bundle size
* Flag deprecated or risky packages

---

## Output Requirements

* Organize findings by **Backend** and **Frontend**
* Reference **file names and line numbers** for all issues
* Classify issues by **Critical / High / Medium / Low**
* Provide **actionable recommendations** with examples
* End with a **Final Summary** containing:

  * Top 5 critical risks (backend + frontend)
  * Quick wins (low effort, high impact)
  * Scalability and hardening roadmap
* Store the output in @Planning/ANALYSIS.md

Be opinionated, pragmatic, and precise—review this as if it were a **production system preparing for scale and security audits**.

---