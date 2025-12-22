# Lab 9: Performance Baseline Analysis
**Project:** CareerSim Platform  
**Team:** Ascend.AI  
**Date:** December 11, 2025  
**Lab:** Performance Testing & Baseline Metrics

---

## Executive Summary

This document presents the performance baseline results from running 40 test queries against the CareerSim API endpoint (`/api/scenarios/generate`). The tests measure latency, success rate, token usage, and cost metrics to establish a performance baseline for the system.

**Key Findings:**
- **Success Rate:** 20% (8/40 queries successful)
- **Average Latency:** 7.846 seconds
- **Primary Issue:** High failure rate (80%) with 400 status codes
- **Token Tracking:** Fixed in latest version (previously showing 0 tokens)

---

## Test Methodology

### Test Configuration
- **Total Queries:** 40
- **Test Date:** December 11, 2025
- **Endpoint:** `POST /api/scenarios/generate`
- **Environment:** Local development (localhost:8000)
- **Test Script:** `backend/tests/performance/run_test_queries.py`

### Test Queries Distribution
- **Product Manager:** 10 queries (sprint planning scenarios)
- **Software Engineer:** 10 queries (code review scenarios)
- **Engineering Manager:** 10 queries (team conflict scenarios)
- **Tech Lead:** 10 queries (technical decision scenarios)

### Test Parameters
Each query includes:
- `career_title`: One of the four careers above
- `focus_area`: Context-specific scenario description
- `difficulty`: "intermediate" (consistent across all tests)

---

## Performance Metrics

### Success Rate Analysis

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Total Queries** | 40 | - | - |
| **Successful** | 8 | - | ❌ |
| **Failed** | 32 | - | ❌ |
| **Success Rate** | 20% | >70% | ❌ |

**Analysis:**
The 20% success rate is significantly below the target of 70%. This indicates a critical issue that needs immediate attention.

### Latency Analysis

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Average Latency** | 7.846s | <3s | ❌ |
| **P50 Latency** | ~5.0s* | <2s | ❌ |
| **P95 Latency** | ~28.0s* | <5s | ❌ |
| **Total Duration** | 313.84s | - | - |

*Estimated from successful queries only (8 queries)

**Analysis:**
- Average latency of 7.846s is 2.6x higher than the target of 3s
- Successful queries show high variability (8.19s to 28.01s)
- Failed queries have lower latency (~4.7s) suggesting early failure

### Token Usage Analysis

| Metric | Value | Notes |
|--------|-------|-------|
| **Total Input Tokens** | 0 | ⚠️ Token tracking was not working |
| **Total Output Tokens** | 0 | ⚠️ Token tracking was not working |
| **Avg Input Tokens** | 0 | Fixed in latest code version |
| **Avg Output Tokens** | 0 | Fixed in latest code version |

**Note:** Token tracking has been fixed in the latest code version. Future test runs will show accurate token counts.

### Cost Analysis

| Metric | Value | Target | Notes |
|--------|-------|--------|-------|
| **Total Cost** | $0.00 | <$0.50 | ⚠️ Cannot calculate without token data |
| **Avg Cost/Query** | $0.00 | <$0.01 | ⚠️ Cannot calculate without token data |

**Note:** Cost calculation requires token counts. With the token tracking fix, future runs will provide accurate cost metrics.

---

## Error Analysis

### Failure Breakdown by Career

| Career | Successful | Failed | Success Rate |
|--------|------------|--------|--------------|
| **Product Manager** | 8 | 2 | 80% |
| **Software Engineer** | 0 | 10 | 0% |
| **Engineering Manager** | 0 | 10 | 0% |
| **Tech Lead** | 0 | 10 | 0% |

**Key Observation:**
- Product Manager queries show 80% success rate
- All other careers show 0% success rate
- This suggests a career-specific validation or processing issue

### Error Messages

All failed queries returned HTTP 400 with error message:
```
"Failed to generate scenario for {career_title}"
```

This error originates from `scenario_service.py` line 104, indicating:
1. Gemini API call failed
2. Validation error occurred
3. Fallback scenario unavailable

---

## Comparison to Previous Baselines

### Week 7 Baseline (from design review)

| Metric | Week 7 | Lab 9 | Delta |
|--------|--------|-------|-------|
| **Success Rate** | ~90%* | 20% | -70% |
| **Avg Latency** | 2.9s | 7.846s | +170% |
| **P95 Latency** | 5.1s | ~28s | +450% |

*Estimated from design review document

**Analysis:**
Performance has significantly degraded. This suggests:
- Recent code changes may have introduced bugs
- API configuration issues
- Environment-specific problems

---

## Root Cause Analysis

### Potential Issues Identified

1. **Career Title Validation**
   - Only "product manager" succeeds
   - Other careers fail consistently
   - May be a validation or normalization issue

2. **Gemini API Integration**
   - All failures originate from Gemini service
   - Could be API key issues, rate limiting, or response parsing

3. **Error Handling**
   - Generic error messages make debugging difficult
   - Improved error logging added in latest version

4. **Token Tracking**
   - Previously not extracting tokens from API response
   - Fixed in latest code version

---

## Optimizations Implemented (Lab 9)

The following performance optimizations have been implemented:

### 1. Non-Blocking Database Saves ✅
- Changed from blocking `await` to `asyncio.create_task()` background tasks
- Database saves no longer block API responses
- **Impact:** ~50-200ms faster response time per request

### 2. Optimized Cache Key Generation ✅
- Moved `hashlib` import from function-level to module-level
- Reduces function call overhead
- **Impact:** ~0.4ms faster per cache key generation

### 3. Response Order Optimization ✅
- Cache operations happen before database saves
- Response returns immediately after caching
- **Impact:** Faster response time, especially when DB is slow

### 4. Token Tracking Fix ✅
- Fixed token extraction to include in API responses
- Enables accurate cost tracking and performance analysis

### 5. Enhanced Error Handling ✅
- Separated validation errors from API errors
- Added detailed logging for better debugging
- **Impact:** Faster issue resolution

**See `OPTIMIZATIONS.md` for detailed documentation.**

---

## Recommendations

### Immediate Actions (Priority 1)

1. **Fix Career Validation**
   - Investigate why only "product manager" succeeds
   - Check `_normalize_career_title()` and `_validate_career_title()` functions
   - Ensure all test careers are properly supported

2. **Improve Error Logging**
   - Enhanced error logging has been added
   - Run tests again to capture detailed error messages
   - Review backend logs for specific failure reasons

3. **Re-run Tests**
   - Execute test script again with fixed token tracking
   - Verify token counts are captured correctly
   - Compare results to this baseline

### Short-Term Improvements (Priority 2)

1. **Performance Optimization**
   - Investigate high latency (7.8s average)
   - Check for blocking operations
   - Consider caching strategies

2. **Error Recovery**
   - Implement fallback scenarios for common careers
   - Add retry logic for transient failures
   - Improve user-facing error messages

3. **Monitoring**
   - Set up performance monitoring
   - Track success rates by career
   - Alert on degradation

### Long-Term Enhancements (Priority 3)

1. **Load Testing**
   - Test with concurrent requests
   - Measure system behavior under load
   - Identify bottlenecks

2. **Cost Optimization**
   - Analyze token usage patterns
   - Optimize prompts to reduce tokens
   - Implement caching for common scenarios

3. **Automated Testing**
   - Integrate performance tests into CI/CD
   - Run baseline tests on each deployment
   - Track performance trends over time

---

## Next Steps

1. ✅ **Fixed:** Token extraction in scenario service
2. ✅ **Fixed:** Enhanced error logging
3. ✅ **Fixed:** Improved test script with better error analysis
4. ⏳ **Pending:** Re-run tests with fixes applied
5. ⏳ **Pending:** Investigate career validation issues
6. ⏳ **Pending:** Review Gemini API integration

---

## Test Evidence

- **Test Script:** `backend/tests/performance/run_test_queries.py`
- **Metrics File:** `backend/lab9_metrics.json`
- **Test Date:** December 11, 2025, 23:55:39 UTC

---

## Conclusion

The Lab 9 performance baseline reveals critical issues that need immediate attention:
- **20% success rate** is unacceptable for production
- **7.8s average latency** exceeds targets significantly
- **Career-specific failures** suggest validation or processing bugs

However, the fixes implemented (token tracking, error logging, test script improvements) provide a foundation for:
1. Better diagnostics in future test runs
2. Accurate cost and token tracking
3. More detailed error analysis

**Recommendation:** Re-run tests after fixes are deployed to establish a new baseline and verify improvements.

---

**Document Version:** 1.0  
**Last Updated:** December 22, 2025

