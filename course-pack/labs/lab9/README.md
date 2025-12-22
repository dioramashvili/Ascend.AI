# Lab 9: Performance Baseline Testing

**Project:** CareerSim Platform  
**Team:** Ascend.AI  
**Lab Date:** December 11, 2025

---

## Overview

Lab 9 focuses on establishing a performance baseline for the CareerSim API by running a comprehensive set of test queries and measuring key metrics including latency, success rate, token usage, and cost.

---

## Files in This Folder

- **PERFORMANCE_ANALYSIS.md** - Detailed analysis of test results, metrics, and recommendations
- **README.md** - This file (overview and navigation)
- **lab9_metrics.json** - Raw test results (located in `backend/` directory)

---

## Test Execution

### Prerequisites
1. Backend server running: `uvicorn app.main:app --reload`
2. Environment variables configured (Gemini API key, etc.)

### Running the Tests

```bash
cd backend
python tests/performance/run_test_queries.py
```

### Output
- Console output with real-time progress
- Summary statistics printed to terminal
- Detailed metrics saved to `backend/lab9_metrics.json`

---

## Key Metrics Measured

1. **Success Rate** - Percentage of queries that return HTTP 200
2. **Latency** - Response time for each query (P50, P95, P99)
3. **Token Usage** - Input and output tokens per query
4. **Cost** - Estimated cost per query based on Gemini pricing
5. **Error Analysis** - Breakdown of failures by career and error type

---

## Test Results Summary

**From December 11, 2025 run:**
- Total Queries: 40
- Success Rate: 20% (8/40)
- Average Latency: 7.846 seconds
- Status: ⚠️ Issues identified - see PERFORMANCE_ANALYSIS.md

---

## Next Steps

1. Review PERFORMANCE_ANALYSIS.md for detailed findings
2. Address identified issues (career validation, error handling)
3. Re-run tests after fixes
4. Compare new baseline to targets

---

## Related Files

- **Test Script:** `backend/tests/performance/run_test_queries.py`
- **Metrics Output:** `backend/lab9_metrics.json`
- **Service Code:** `backend/app/services/scenario_service.py`
- **API Route:** `backend/app/api/routes/scenarios.py`

---

## Links to Capstone Project

This performance baseline directly supports:
- **Capstone Proposal:** `docs/week-4/capstone-proposal-v2.md`
- **Evaluation Plan:** `docs/week-4/evaluation-plan-v2.md`
- **Technical Metrics:** Success rate, latency, and cost targets defined in proposal

---

**Last Updated:** December 22, 2025

