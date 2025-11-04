# Function Specification Document

**Team Name:** AI Career Simulation Team  
**Project:** CareerSim Platform  
**Date:** 2025-11-04  

---

## Overview

**Number of Functions:** 3  

**Purpose of Function Calling in Our Project:**

Our AI system uses function calling to dynamically generate interactive career simulations, evaluate user responses through Gemini AI, and manage asynchronous task results via Redis and Celery.  
This enables a smooth, state-aware conversational experience between the user and the backend.

---

## Function Calling Flow

```
1. User Query → AI receives message
2. AI Decision → Determines if function call needed
3. Function Call → AI generates {"function": "generate_career_scenario", "arguments": {"career_title": "data analyst"}}
4. OUR CODE executes → FastAPI endpoint queries Redis/Gemini and returns JSON
5. Function Result → We send result back to AI
6. AI Response → AI synthesizes natural-language answer with function data
7. User Sees Result → "You are working as a data analyst at a fintech company..."
```

**Critical Point:** The LLM does **not** execute the functions directly — it only decides **which** function to call and **with what parameters**.  
Execution, validation, and persistence happen in our FastAPI backend.

---

## Function 1: `generate_career_scenario`

### Basic Information

**Function Name:** `generate_career_scenario`  
**Purpose:** Generates a personalized career scenario for a given career title using Gemini AI, caching results in Redis.  

**When AI Should Call This:**
- When a user selects or types a career title  
- When the system needs to create or fetch a cached simulation scenario  

### Parameters

| Parameter | Type | Required | Validation | Description |
|------------|------|----------|-------------|-------------|
| `career_title` | string | Yes | 3–100 chars, lowercase, alphanumeric/spaces | The user-selected or typed career name |
| `prompt_version` | string | No | default: `"v1"` | Specifies which AI prompt template version to use |

### Return Structure

**On Success**
```json
{
  "status": "success",
  "data": {
    "career_title": "software engineer",
    "scenario": "You are leading a small dev team...",
    "options": ["Refactor codebase", "Deploy hotfix", "Delay release"]
  }
}
```

**On Error**
```json
{
  "status": "error",
  "error_code": "GENERATION_FAILED",
  "error_message": "Unable to generate scenario for given title."
}
```

### JSON Schema
```json
{
  "name": "generate_career_scenario",
  "description": "Generates a personalized career scenario for a given career title using Gemini AI, returning scenario text and decision options. Results are cached for reuse.",
  "parameters": {
    "type": "object",
    "properties": {
      "career_title": {
        "type": "string",
        "description": "The user-selected or typed career name (3-100 lowercase alphanumeric characters)"
      },
      "prompt_version": {
        "type": "string",
        "description": "Version of the prompt template to use (default: v1)",
        "default": "v1"
      }
    },
    "required": ["career_title"]
  }
}
```

### Implementation Pseudocode
```python
@cache_response(ttl=3600)
async def generate_career_scenario(career_title: str, prompt_version: str = "v1"):
    # 1) Validate
    if not isinstance(career_title, str) or len(career_title.strip()) < 3:
        return {"status": "error", "error_code": "INVALID_INPUT", "error_message": "career_title too short"}
    # 2) Load prompt by version (DB)
    # 3) Call Gemini with retries and timeout
    # 4) Shape response and cache via decorator
    return {
        "status": "success",
        "data": {"career_title": career_title, "scenario": "...", "options": ["A", "B", "C"]}
    }
```

### Example Usage
**User Input:**  
> “Generate a simulation for a data analyst.”

**AI Generates:**  
```json
{
  "function": "generate_career_scenario",
  "arguments": {"career_title": "data analyst"}
}
```

**Function Returns:**  
```json
{
  "status": "success",
  "data": { "career_title": "data analyst", "scenario": "...", "options": ["A","B","C"] }
}
```

### Safety Considerations
- Validate `career_title` format before Gemini call  
- Sanitize input strings  
- Apply rate-limiting (10/min per IP)  
- Handle Gemini timeouts gracefully  

---

## Function 2: `evaluate_user_response`

### Basic Information

**Function Name:** `evaluate_user_response`  
**Purpose:** Evaluates the user’s choice within a scenario using Gemini AI via a Celery background task, providing score and feedback.  

**When AI Should Call This:**
- After user selects an option or submits an answer  
- When an evaluation or feedback is required  

### Parameters

| Parameter | Type | Required | Validation | Description |
|------------|------|----------|-------------|-------------|
| `career_title` | string | Yes | 3–100 chars | The active career scenario |
| `user_answer` | string | Yes | 1–500 chars | User’s response or selected option |
| `session_id` | string | Yes | UUID | Unique session identifier |
| `task_mode` | enum | No | ["sync", "async"], default `"async"` | Evaluation mode |

### Return Structure

**On Success (Async)**
```json
{
  "status": "pending",
  "data": {
    "task_id": "8d9a32bf-76b3-4f9a-bc9d-2c77a46a8c3f",
    "message": "Evaluation task queued."
  }
}
```

**On Error**
```json
{
  "status": "error",
  "error_code": "EVALUATION_FAILED",
  "error_message": "Gemini API failed or task could not be queued."
}
```

### JSON Schema
```json
{
  "name": "evaluate_user_response",
  "description": "Evaluates a user's response for a given career scenario using Gemini AI. Supports asynchronous task execution via Celery and returns a task ID for polling.",
  "parameters": {
    "type": "object",
    "properties": {
      "career_title": { "type": "string", "description": "Career title related to the scenario" },
      "user_answer": { "type": "string", "description": "User's answer text (1–500 chars)" },
      "session_id": { "type": "string", "description": "Unique session identifier (UUID)" },
      "task_mode": {
        "type": "string",
        "enum": ["sync", "async"],
        "default": "async",
        "description": "Evaluation mode (sync for immediate result, async for background task)"
      }
    },
    "required": ["career_title", "user_answer", "session_id"]
  }
}
```

### Implementation Pseudocode
```python
@app.post("/evaluate")
async def evaluate_user_response(data: EvaluationRequest, user=Depends(get_current_user)):
    # 1) Validate & auth already handled by Pydantic/JWT dependencies
    # 2) Dispatch Celery task
    task = evaluate_user_choice_task.delay(data.career_title, data.user_answer)
    return {"status": "pending", "data": {"task_id": task.id, "message": "Evaluation task queued."}}
```

### Example Usage
**User Input:**  
> “I’d refactor the codebase to improve structure.”

**AI Generates:**  
```json
{
  "function": "evaluate_user_response",
  "arguments": {
    "career_title": "software engineer",
    "user_answer": "Refactor the codebase to improve structure.",
    "session_id": "ad1e93c7-6fbb-46fa-8a3b-dcbb6f308a90"
  }
}
```

### Safety Considerations
- Validate input via Pydantic models  
- Use JWT authentication for authorized sessions  
- Queue isolation per user to avoid leakage  
- Log all evaluations with timestamp & user_id  

---

## Function 3: `get_task_result`

### Basic Information

**Function Name:** `get_task_result`  
**Purpose:** Fetches the result of an ongoing background evaluation task (Celery) from Redis.  

**When AI Should Call This:**
- When user asks for feedback or result  
- Periodically polls task result in async flows  

### Parameters

| Parameter | Type | Required | Validation | Description |
|------------|------|----------|-------------|-------------|
| `task_id` | string | Yes | UUID format | The ID returned from `evaluate_user_response` |

### Return Structure

**On Success**
```json
{
  "status": "success",
  "data": {
    "feedback": "Your decision shows great leadership...",
    "score": 9
  }
}
```

**On Pending**
```json
{ "status": "pending", "data": {} }
```

**On Error**
```json
{
  "status": "error",
  "error_code": "TASK_NOT_FOUND",
  "error_message": "No task found with this ID."
}
```

### JSON Schema
```json
{
  "name": "get_task_result",
  "description": "Retrieves the result of an asynchronous evaluation task from Redis using its task ID.",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": { "type": "string", "description": "Celery task ID (UUID format)" }
    },
    "required": ["task_id"]
  }
}
```

### Implementation Pseudocode
```python
@app.get("/tasks/{task_id}")
async def get_task_result(task_id: str, user=Depends(get_current_user)):
    result = celery_app.AsyncResult(task_id)
    if result.state == "PENDING":
        return {"status": "pending", "data": {}}
    elif result.state == "SUCCESS":
        # Optionally assert task ownership via session mapping
        return {"status": "success", "data": result.result}
    else:
        return {"status": "error", "error_code": "TASK_NOT_FOUND", "error_message": "Task not found or failed."}
```

---

## Function Calling Implementation Plan

### Week 6: Basic Implementation
- [ ] Set up OpenAI function calling with one simple function  
- [ ] Test the complete loop (query → function call → result → response)  
- [ ] Handle basic errors  

### Week 7: Full Implementation
- [ ] Implement all 2–3 functions  
- [ ] Add proper error handling for each  
- [ ] Implement authorization/validation  

### Week 8: Polish & Testing
- [ ] Test edge cases (invalid inputs, missing data, etc.)  
- [ ] Optimize performance (caching, batching)  
- [ ] Add logging and monitoring  

---

## Error Code Reference

Document all error codes your functions might return:

| Error Code | HTTP Status | Meaning | User-Facing Message |
|------------|------------:|---------|---------------------|
| INVALID_INPUT | 400 | Input validation failed | "Please enter a valid value." |
| UNAUTHORIZED | 403 | Token missing / invalid or resource not owned | "You don't have permission to perform this action." |
| GENERATION_FAILED | 502 | Gemini generation failed or timed out | "Couldn't generate a scenario right now. Please try again." |
| EVALUATION_FAILED | 502 | Gemini evaluation failed or task dispatch failed | "We couldn't evaluate your answer. Please try again." |
| TASK_NOT_FOUND | 404 | Task ID doesn't exist or expired | "We can't find that task result yet." |
| RATE_LIMITED | 429 | Rate limit exceeded | "You're doing that too often. Please slow down." |
| DATABASE_ERROR | 500 | Database connection or query failed | "We're having technical difficulties. Try again soon." |

---

## Testing Strategy

### Unit Tests

For each function, test:

- [ ] Valid inputs → correct output  
- [ ] Invalid inputs → proper error messages  
- [ ] Missing required parameters → error  
- [ ] Authorization failures → unauthorized error  
- [ ] Database/API failures → graceful degradation  

**Example Unit Tests (pytest-style):**
```python
def test_generate_valid(monkeypatch):
    from app.functions import generate_career_scenario
    res = asyncio.run(generate_career_scenario("software engineer"))
    assert res["status"] == "success"
    assert "scenario" in res["data"]

def test_generate_invalid_short():
    res = asyncio.run(generate_career_scenario("se"))
    assert res["status"] == "error"
    assert res["error_code"] == "INVALID_INPUT"

def test_evaluate_queues_task(client, auth_headers):
    payload = {"career_title": "software engineer", "user_answer": "Refactor", "session_id": "00000000-0000-0000-0000-000000000001"}
    r = client.post("/evaluate", json=payload, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "pending"
```

### Integration Tests

Test the full loop:

- [ ] User query → AI generates function call → Our code executes → AI responds  
- [ ] Multiple function calls in sequence  
- [ ] Error recovery (what if function fails?)  

**Flow Test (pseudo):**
```python
# 1) generate
gen = client.post("/generate-scenario", json={"career_title": "data analyst"}).json()
# 2) evaluate
ev = client.post("/evaluate", json={"career_title": "data analyst", "user_answer": "Choose A", "session_id": "..."}).json()
# 3) poll
poll = client.get(f"/tasks/{ev['data']['task_id']}").json()
```

---

## Performance Metrics

**Target Performance:**
- Function execution time (backend only): < 200 ms (cached), < 800 ms (uncached)  
- Total query time (including LLM): < 2 seconds (p95)  
- Success rate: > 99%  
- Error rate: < 1%  

**Monitoring:**
- [ ] Log every function call (function name, parameters hash, result, latency)  
- [ ] Track success vs error rates  
- [ ] Alert if function latency > 500 ms (uncached)  
- [ ] Dashboard showing function usage stats (per endpoint, per user)  

---

## Resources

**API Documentation:**
- OpenAI Function Calling: https://platform.openai.com/docs/guides/function-calling  
- Anthropic Tool Use: https://docs.anthropic.com/claude/docs/tool-use  

**Libraries:**
- OpenAI / Vertex AI SDKs (as applicable), FastAPI, Pydantic, Celery, Redis (redis-py), SQLAlchemy, Tenacity, structlog, Sentry SDK

---

## Team Responsibilities

- Function 1 implementation: Toma Danelia  
- Function 2 implementation: Davit Ioramashvili  
- Function 3 implementation: Temuri Machavariani  
- Testing & validation: Sopo Mrelashvili 

---

## Sign-off

**Team Members:**
- Toma Danelia - Backend integration and Gemini scenario generation logic
- Davit Ioramashvili - Async evaluation flow, Celery tasks, and AI response scoring
- Temuri Machavariani - Frontend polling and result visualization
- Sopo Mrelashvili - Test planning, validation, and QA coordination 

**Date Completed:** 2025-11-04

**Reviewed By Instructor:** [ ] Yes  [ ] No  [Date: _____ ]

---

## Appendix: Common Patterns

**Pattern 1: Search Functions**  
Use when the AI needs to search through data.  
*Example:* `search_documents(query, filters, max_results)`

**Pattern 2: CRUD Functions**  
Use when the AI needs to create, read, update, or delete records.  
*Example:* `update_ticket(ticket_id, status, notes)`

**Pattern 3: Calculation Functions**  
Use when the AI needs to perform calculations.  
*Example:* `calculate_shipping(origin, destination, weight)`

**Pattern 4: Validation Functions**  
Use when the AI needs to check if something is valid.  
*Example:* `validate_coupon_code(code, user_id)`

**Pattern 5: Escalation Functions**  
Use when the AI needs to hand off to humans.  
*Example:* `escalate_to_human(ticket_id, reason, priority)`
