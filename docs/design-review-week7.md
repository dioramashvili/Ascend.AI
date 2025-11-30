# Design Review: Week 7
Team Name: AscendAI
Project Title: CareerSim Platform
Team Members: Sopo Mrelashvili, Toma Danelia, Davit Ioramashvili, Temo Machavariani
Date: 2025-11-30
Repository: https://github.com/dioramashvili/Ascend.AI

## Executive Summary
During Weeks 3–7, the CareerSim Platform has evolved into a functional AI-powered career simulation assistant. The system now supports dynamic scenario generation, response evaluation, structured event logging, and stable LLM-driven interactions. Most core infrastructure components are implemented, including frontend–backend communication, function calling, and Supabase persistence.

The current state of the system is strong, with all Week 6 requirements completed and Week 7 schema design finalised. Some performance limitations remain, mostly related to API latency, error handling consistency, and concurrency tolerance.

The team is **conditionally ready** for Week 8 agent orchestration. The foundation is solid but requires completion of critical improvements listed below.

### Critical Actions Before Week 8
1. Improve concurrency handling and request timeouts.
2. Finalise error-handling consistency across backend modules.
3. Add cost-control measures and logging around LLM tool usage.

---

## 1. Architecture Validation

### 1.1 System Architecture Diagram

**Architecture Overview (Textual Diagram Substitute):**
- **Frontend (React / Vite)**  
  Sends user inputs → Receives structured responses → Renders simulation UI.
- **Backend (FastAPI, Python)**  
  Handles API routing, validation, event schema enforcement, LLM orchestration, and database I/O.
- **Supabase (PostgreSQL)**  
  Stores scenarios, evaluations, user attempts, sessions.
- **OpenAI GPT‑4.1 Mini & GPT‑4.1**  
  Used for scenario generation, evaluation, and assistant responses.
- **Event Logging Layer**  
  Stores JSON-schema–validated logs for observability.
- **Local Development Tooling**  
  Python virtual environment, Pydantic models, test suite.

### 1.2 Component Descriptions

#### **Frontend**
- **Technology:** React + Vite  
- **Purpose:** Display career scenarios, collect user answers, show evaluations.  
- **Status:** Working  
- **Key Features:**
  - Clean user interface for simulation steps  
  - Input collection and validation  
  - Integration with backend REST endpoints

#### **Backend**
- **Technology:** Python 3.11, FastAPI  
- **Purpose:** Core application logic, LLM communications, schema validation  
- **Status:** Working  
- **Key Features:**
  - REST endpoints for scenario generation and evaluation  
  - Pydantic-based schema validation  
  - OpenAI function calling and structured outputs  
  - Supabase DB integration  
  - Event logging utilities

#### **Database**
- **Technology:** Supabase (PostgreSQL)  
- **Purpose:** Persistent storage for scenarios, user evaluations, logs  
- **Status:** Working  
- **Schema Overview:**  
  - `scenarios`  
  - `evaluations`  
  - `sessions`  
  - `event_logs`

#### **AI/LLM Integration**
- **Models:** GPT‑4.1 Mini, GPT‑4.1  
- **Purpose:** Scenario generation, response evaluation, tool-calling logic  
- **Status:** Working  
- **Capabilities:**  
  - Function calling  
  - JSON formatting  
  - Follow-up questioning logic  
  - Scenario difficulty scaling

### 1.3 Data Flow Description
1. User submits a prompt in frontend.  
2. Frontend sends request → FastAPI `/generate_scenario`.  
3. Backend validates payload via Pydantic.  
4. Backend triggers LLM call (model = GPT‑4.1).  
5. LLM may call defined tools (e.g., `save_evaluation`).  
6. Backend processes and logs event payloads.  
7. Supabase stores scenario/evaluation.  
8. Backend returns structured JSON response to frontend.  
9. Frontend displays results.

### 1.4 Changes from Week 2 Proposal

| Aspect | Week 2 Proposal | Week 7 Reality | Reason |
|-------|------------------|----------------|--------|
| LLM Model | GPT‑4 Turbo | GPT‑4.1 Mini + GPT‑4.1 | Cost optimisation |
| Database | Local JSON | Supabase PostgreSQL | Needed persistence |
| Context handling | Stateless | Session-aware | Better UX |
| Logging | Minimal | Full event schema logging | Observability requirements |

#### Lessons Learned
- Full schema validation early prevents major debugging pain later.  
- Function calling simplifies backend logic but increases cost.  
- Database schema must be designed before Week 6 to avoid rewriting code.

---

## 2. Event Schema Documentation
Full schemas are stored in:  
📄 `docs/event-schemas-full.md`

### 2.1 Core Event Schemas
This design review includes three excerpts (full version in file):

#### User Input Event (Excerpt)
```json
{
  "event_type": "user_input",
  "timestamp": "2025-11-30T10:30:00Z",
  "request_id": "req_91ad038fa91c",
  "user_query": "Generate a career scenario for a junior software engineer.",
  "user_id": "user_sopo",
  "session_id": "session_001"
}
```

(Additional schemas: LLM Request, LLM Response, Error Event, Tool Call, Tool Result, Database Write Event)

### 2.2 Schema Validation Rules
- All events validated through Pydantic models.  
- Required fields: `event_type`, `timestamp`, `request_id`.  
- Constraints:  
  - `user_query` max length = 500  
  - enums for event types  
  - ISO 8601 timestamps  

---

## 3. Smoke Test Results

### 3.1 Test Summary
- **Total tests:** 18  
- **Passed:** 16  
- **Failed:** 2  
- **Skipped:** 0  
- **Date:** 2025-11-29  

### 3.2 Detailed Results

#### ✅ PASS: End-to-End Scenario Generation
- `req_1029abc` → Response in **1.9s**  
- Tokens: 160 input, 58 output  
- LLM function call: none  
- Status: Working reliably  

#### ❌ FAIL: 10-concurrent-request stress test
- 10 requests →  
  - 6 succeeded  
  - 4 timed out (30s)  
- Average latency (success): **11.4s**  
- Cause: Backend waiting on sequential LLM calls  

**Mitigation:** Enable batching and async workers.

#### ❌ FAIL: Error propagation missing on DB write failure
- Missing error return → 500 returned to frontend  
- Fix: Add structured error event + retry logic  

### 3.3 Evidence Files
Stored in: `docs/evidence/`  
- smoke-test-results.txt  
- error-log-samples.json  
- performance.csv  

---

## 4. Performance Baseline

### 4.1 Test Methodology
- Date: 2025-11-29  
- Sample size: 25 queries  
- Environment: macOS M2, 300 Mbps internet  

### 4.2 Latency Analysis

| Metric | Value | Target | Status |
|--------|--------|---------|--------|
| p50 | 2.3s | <3s | ✅ |
| p95 | 5.1s | <6s | ✅ |
| p99 | 10.8s | <12s | ✅ |
| Average | 2.9s | <4s | ✅ |

### 4.3 Token Usage

| Metric | Value |
|--------|--------|
| Avg input tokens | 118 |
| Avg output tokens | 92 |
| Total | 210 |
| Variability | Moderate |

### 4.4 Cost Analysis

| Component | Cost/Req |
|-----------|-----------|
| LLM | $0.0021 |
| Supabase | $0.0000 |
| Total | **$0.0021** |

Projected Monthly Cost (1000 users/day):  
→ **$63/month**

### 4.5 Comparison to Week 2

| Metric | Week 2 Estimate | Week 7 Actual | Delta |
|--------|------------------|----------------|--------|
| Latency | 3s | 2.9s | -3% |
| Cost | $0.003 | $0.0021 | -30% |
| Tokens | 300 | 210 | -30% |

---

## 5. Hypothesis Validation

### 5.1 Hypothesis
*"Users produce higher‑quality answers when scenarios include role‑specific constraints."*

### 5.2 Method
- Control: 25 unconstrained scenarios  
- Treatment: 25 constrained scenarios  
- Evaluation: LLM rubric scoring (0–10)

### 5.3 Results

| Condition | Avg Score | Sample Size |
|-----------|-----------|--------------|
| No constraints | 5.8 | 25 |
| With constraints | 7.4 | 25 |
| Delta | **+1.6** | — |

### 5.4 Conclusion
- Hypothesis **supported**  
- Constrained scenarios yield **~27% better performance**

### 5.5 Supporting Data
Stored in: `docs/evidence/hypothesis-tests/`

---

## 6. Readiness Assessment

### 6.1 Overall Status: **YELLOW – Conditionally Ready**

### 6.2 Detailed Assessment

#### Can system handle 20x API calls?  
→ **No** (latency too high)

#### Error handlers robust?  
→ **Partially** (DB write errors need consistency)

#### Cost model sustainable?  
→ **Yes**

### Critical Issues (Must Fix)
1. Concurrency limits – High – Due: Dec 2  
2. DB error propagation – High – Due: Dec 2  

### Important Issues (Should Fix)
3. Add request batching – Medium – Due: Dec 4  
4. Add cost logging – Medium – Due: Dec 5  

### Nice-to-Have
5. Add UI session timeline – Low – Due: Dec 7  

---

## 6.3 Action Plan

| Task | Severity | Owner | Deadline | Status |
|-------|-----------|--------|-----------|---------|
| Improve concurrency handling | Critical | Davit | Dec 2 | In Progress |
| DB error schema logging | Critical | Toma | Dec 2 | Not Started |
| Implement LLM batching | Important | Sopo | Dec 4 | Not Started |
| Cost monitoring | Important | Temo | Dec 5 | Not Started |

---

## 6.4 Contingency Plans
- If concurrency fixes fail, use **queued agent orchestration** for Week 8.  
- If DB issues persist, fallback to **local JSON logs**.  

---

## 6.5 Team Commitments
All members commit to preparing the system for Week 8 agent orchestration.

Signatures:
- **Sopo:** Committed  
- **Toma:** Committed  
- **Davit:** Committed  
- **Temo:** Committed  

---

## Appendix
### A. Complete Event Schemas  
See: `docs/event-schemas-full.md`

### B. Smoke Test Evidence  
See: `docs/evidence/`

### C. Performance Raw Data  
See: `docs/performance.csv`

### D. Hypothesis Test Data  
See: `docs/hypothesis-tests/`

### E. High-Resolution Architecture Diagram  
(Not included—text-based description provided.)

---

### Document Change Log

| Date | Version | Changes | Author |
|------|----------|-----------|---------|
| 2025-11-30 | 1.0 | Initial Week 7 Design Review | AscendAI Team |

