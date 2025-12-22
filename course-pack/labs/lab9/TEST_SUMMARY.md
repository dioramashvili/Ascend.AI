# Lab 9: Test Execution Summary

**Date:** December 11, 2025  
**Test Script:** `backend/tests/performance/run_test_queries.py`  
**Total Queries:** 40

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Success Rate** | 20% (8/40) |
| **Failure Rate** | 80% (32/40) |
| **Avg Latency** | 7.846s |
| **Total Duration** | 313.84s (~5.2 minutes) |

---

## Test Query Breakdown

### By Career Type

| Career | Queries | Successful | Failed | Success Rate |
|--------|---------|------------|--------|--------------|
| Product Manager | 10 | 8 | 2 | 80% ✅ |
| Software Engineer | 10 | 0 | 10 | 0% ❌ |
| Engineering Manager | 10 | 0 | 10 | 0% ❌ |
| Tech Lead | 10 | 0 | 10 | 0% ❌ |

### By Focus Area

| Focus Area | Queries | Successful | Failed |
|------------|---------|------------|--------|
| Sprint Planning | 10 | 8 | 2 |
| Code Review | 10 | 0 | 10 |
| Team Conflict | 10 | 0 | 10 |
| Technical Decision | 10 | 0 | 10 |

---

## Successful Queries

Only Product Manager queries succeeded. All successful queries:
- Career: "product manager"
- Focus: "sprint planning"
- Status: HTTP 200
- Latency range: 8.19s - 33.52s

---

## Failed Queries

All failures returned HTTP 400 with error:
```
"Failed to generate scenario for {career_title}"
```

**Failure Pattern:**
- All "software engineer" queries failed
- All "engineering manager" queries failed  
- All "tech lead" queries failed
- 2 "product manager" queries failed

**Common Characteristics:**
- Lower latency (~4.7s) suggesting early failure
- Consistent error message
- No token usage (0 tokens)

---

## Latency Analysis

### Successful Queries Only (8 queries)

| Statistic | Value |
|-----------|-------|
| Min | 8.19s |
| Max | 33.52s |
| Average | ~15.5s |
| Median | ~9.5s |

### Failed Queries (32 queries)

| Statistic | Value |
|-----------|-------|
| Min | 4.65s |
| Max | 5.18s |
| Average | ~4.7s |

**Observation:** Failed queries fail faster (~4.7s) than successful queries complete (~15.5s average).

---

## Issues Identified

1. ✅ **Fixed:** Token tracking not working (now fixed in code)
2. ✅ **Fixed:** Poor error messages (enhanced logging added)
3. ⚠️ **Open:** Career validation failing for 3/4 careers
4. ⚠️ **Open:** High latency even for successful queries
5. ⚠️ **Open:** 80% failure rate unacceptable

---

## Recommendations

1. **Immediate:** Investigate career validation logic
2. **Immediate:** Re-run tests after fixes
3. **Short-term:** Add fallback scenarios
4. **Short-term:** Optimize latency
5. **Long-term:** Set up automated performance monitoring

---

## Files Generated

- `lab9_metrics.json` - Complete test results with all 40 queries
- `PERFORMANCE_ANALYSIS.md` - Detailed analysis and recommendations
- `TEST_SUMMARY.md` - This file (quick reference)

---

**Last Updated:** December 22, 2025

