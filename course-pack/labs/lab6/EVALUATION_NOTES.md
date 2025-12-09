# Evaluation Notes  
**Lab 6: Function Calling & Structured Outputs**  
**Project:** CareerSim Platform  
**Team:** Ascend.AI 

---

## Functions Tested
1. `generate_career_scenario(career_title, prompt_version)`  
2. `evaluate_user_response(career_title, user_answer, session_id, task_mode)`  
3. `save_evaluation(user_id, scenario_id, user_answer, score, feedback)`  

---

## Test Summary

### 1. `generate_career_scenario`

| Test | Input | Expected | Got | Time (s) | Pass |
|------|--------|-----------|------|----------|------|
| 1 | `"software engineer"` | Valid scenario + 3 options | Scenario text + 3 options | 0.42 | ✅ |
| 2 | `"data analyst"` | Valid scenario + 3 options | Scenario text + 3 options | 0.39 | ✅ |
| 3 | `"se"` | Validation error | `INVALID_INPUT` error | 0.11 | ✅ |

#### Observations
- Average response time: **0.30s cached**, **0.40s uncached**
- Input validation works correctly
- Output always matched JSON schema
- No crashes or timeouts

---

### 2. `evaluate_user_response`

| Test | Input | Expected | Got | Time (s) | Pass |
|------|--------|-----------|------|----------|------|
| 1 | SE scenario + answer | Celery task queued | `status: pending`, `task_id` returned | 0.21 | ✅ |
| 2 | Invalid UUID | Validation error | `INVALID_INPUT` | 0.06 | ✅ |
| 3 | `task_mode="sync"` | Immediate evaluation | Score + feedback | 0.88 | ✅ |

#### Observations
- Async task dispatch works reliably
- Sync mode slower due to Gemini API latency
- Schema validation passed for all tests
- No queue congestion or lost tasks detected

---

### 3. `save_evaluation`

| Test | Input | Expected | Got | Time (s) | Pass |
|------|--------|-----------|------|----------|------|
| 1 | Valid evaluation data | Record saved to Supabase | Record ID returned | 0.27 | ✅ |
| 2 | Missing field (`score`) | Validation error | Error before DB call | 0.04 | ✅ |
| 3 | Invalid `user_id` | Validation error | No DB write attempted | 0.05 | ✅ |
| 4 | Supabase unreachable | Graceful error | `DATABASE_ERROR` | 0.32 | ✅ |

#### Observations
- Data successfully inserted into `evaluations` table
- No duplication issues or inconsistent writes
- Error handling worked correctly
- Fast execution time (avg **0.17s**)

---

## Overall Observations

- All functions matched their JSON schemas with **100% accuracy**
- No unhandled exceptions or malformed outputs
- Average performance within targets
- Celery and Redis behaved as expected
- Scenario caching significantly improved speed (down to **0.18s**)
- Validation logic robust across all tested paths

---

## Next Steps

### Short-Term
- Add stronger validation for empty `user_answer`
- Add more edge-case test coverage
- Implement full workflow tests:

scenario → evaluate → save_evaluation
- Add Supabase mocking for offline/testing environments

### Medium-Term
- Add `metadata` field to `save_evaluation`
- Store scenario text inside evaluation history for traceability
- Create Alembic migration for indexing evaluation history

### Long-Term
- Build unified simulation timeline (evaluation + scenario + user decisions)
- Implement retry logic for failed Supabase writes
- Add instructor analytics dashboard (accuracy trends, difficulty metrics)

---

## Conclusion

All three functions performed reliably under structured output and function-calling conditions.  
The system now fully supports:
- Dynamic scenario generation  
- AI-driven evaluation  
- Persistent storage of evaluation results  

The CareerSim Platform is ready for integration into the end-to-end simulation pipeline.

---


