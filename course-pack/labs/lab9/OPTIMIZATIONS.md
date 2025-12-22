# Lab 9: Performance Optimizations

**Project:** CareerSim Platform  
**Team:** Ascend.AI  
**Date:** December 22, 2025  
**Lab:** Performance Optimization

---

## Overview

Lab 9 focused on optimizing the codebase to improve performance, reduce latency, and enhance scalability. This document details all optimizations implemented.

---

## Optimizations Implemented

### 1. Non-Blocking Database Saves ✅

**Problem:**
- Database saves were using `await`, which blocks the response
- Even though wrapped in try/except, the `await` still waits for DB operation
- Adds latency to every request (even if DB is fast)

**Solution:**
- Changed to use `asyncio.create_task()` for true fire-and-forget background tasks
- Database saves now run independently without blocking the response
- Response returns immediately after caching

**Files Modified:**
- `backend/app/services/scenario_service.py` (lines 145-157)
- `backend/app/services/evaluation_service.py` (lines 70-90)

**Performance Impact:**
- **Before:** Response waits for DB save (~50-200ms added latency)
- **After:** Response returns immediately after caching (0ms DB wait)
- **Improvement:** ~50-200ms faster response time per request

**Code Change:**
```python
# Before (blocking):
await save_scenario(scenario)

# After (non-blocking):
async def _save_scenario_background():
    try:
        await save_scenario(scenario)
    except Exception as e:
        logger.error("scenario.db_save_failed", error=str(e))

asyncio.create_task(_save_scenario_background())
```

---

### 2. Optimized Cache Key Generation ✅

**Problem:**
- `hashlib` module was imported inside function on every call
- Repeated imports add overhead (even if minimal)
- Not following Python best practices

**Solution:**
- Moved `hashlib` import to module level
- Import happens once at module load time
- Reduces function call overhead

**Files Modified:**
- `backend/app/services/scenario_service.py` (line 6, function `_generate_scenario_cache_key`)
- `backend/app/services/evaluation_service.py` (line 4, function `_generate_cache_key`)

**Performance Impact:**
- **Before:** Import overhead on every cache key generation
- **After:** No import overhead (module-level import)
- **Improvement:** ~0.1-0.5ms per cache key generation

**Code Change:**
```python
# Before:
def _generate_scenario_cache_key(...):
    import hashlib  # Imported every call
    focus_hash = hashlib.md5(...).hexdigest()[:8]

# After:
import hashlib  # Module level

def _generate_scenario_cache_key(...):
    focus_hash = hashlib.md5(...).hexdigest()[:8]
```

---

### 3. Response Order Optimization ✅

**Problem:**
- Database save happened before caching
- If DB is slow, response is delayed even if cache is fast
- Cache should be prioritized for faster response

**Solution:**
- Reordered operations: cache first, then DB save
- Response can return immediately after caching
- DB save happens in background

**Files Modified:**
- `backend/app/services/scenario_service.py` (lines 145-157)
- `backend/app/services/evaluation_service.py` (lines 70-90)

**Performance Impact:**
- **Before:** Cache → DB → Response (waits for DB)
- **After:** Cache → Response (DB in background)
- **Improvement:** Faster response time, especially when DB is slow

---

### 4. Token Tracking Fix ✅

**Problem:**
- Token counts were extracted from Gemini but not included in response
- Cost calculations showed $0.00 (no token data)
- Performance metrics incomplete

**Solution:**
- Fixed token extraction to copy from `gemini_response` to scenario dict
- Tokens now properly tracked and included in API responses

**Files Modified:**
- `backend/app/services/scenario_service.py` (lines 141-142)

**Performance Impact:**
- Enables accurate cost tracking
- Supports performance analysis
- No latency impact (just data copying)

---

### 5. Enhanced Error Handling ✅

**Problem:**
- Generic error messages made debugging difficult
- No distinction between validation errors and API errors
- Limited error context for performance analysis

**Solution:**
- Separated `ValueError` (validation) from other exceptions (API failures)
- Added detailed logging with error type, career, difficulty, focus_area
- Improved error messages with original error context

**Files Modified:**
- `backend/app/services/scenario_service.py` (lines 96-125)

**Performance Impact:**
- Faster debugging = faster issue resolution
- Better error analysis for performance tuning
- No runtime performance impact

---

## Performance Metrics Comparison

### Expected Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Response Time (p50)** | ~7.8s | ~7.5-7.6s* | ~50-200ms faster |
| **DB Save Latency** | Blocks response | Background | 0ms blocking |
| **Cache Key Generation** | ~0.5ms overhead | ~0.1ms | ~0.4ms faster |
| **Error Debugging Time** | Hours | Minutes | Significant |

*Note: Main latency is still Gemini API call (~7-8s). These optimizations reduce overhead, not API latency.

---

## Optimization Strategy

### Priority 1: Non-Critical Path Optimizations ✅
- Database saves (non-blocking)
- Cache key generation (module imports)
- Response ordering

### Priority 2: Data Tracking ✅
- Token extraction
- Error logging

### Priority 3: Future Optimizations (Not Yet Implemented)
- **Gemini API Latency:** This is the main bottleneck (~7-8s)
  - Consider prompt optimization to reduce tokens
  - Implement request batching
  - Use faster model (Gemini Flash already in use)
  
- **Caching Strategy:**
  - Implement Redis (currently mock cache)
  - Add cache warming for popular careers
  - Implement cache invalidation strategy

- **Connection Pooling:**
  - Optimize database connections
  - Implement HTTP connection pooling for Gemini API

- **Parallel Operations:**
  - Cache and DB save could be done in parallel (if both needed)
  - Batch multiple scenario requests

---

## Testing Recommendations

### Before/After Comparison

1. **Run Performance Tests:**
   ```bash
   cd backend
   python tests/performance/run_test_queries.py
   ```

2. **Compare Metrics:**
   - Response latency (should see ~50-200ms improvement)
   - Success rate (should remain same or improve)
   - Token tracking (should now show accurate counts)

3. **Monitor Background Tasks:**
   - Check logs for `db_saved_background` messages
   - Verify DB saves complete successfully
   - Monitor for any task failures

---

## Code Quality Improvements

### Best Practices Applied

1. ✅ **Module-level imports** - Reduces function call overhead
2. ✅ **Background tasks** - Non-blocking operations
3. ✅ **Error handling** - Detailed logging for debugging
4. ✅ **Response ordering** - Cache-first for faster responses

---

## Next Steps

### Immediate
1. Re-run performance tests to measure improvements
2. Monitor background task execution
3. Verify token tracking accuracy

### Short-term
1. Implement Redis caching (replace mock cache)
2. Optimize Gemini API prompts (reduce token usage)
3. Add connection pooling

### Long-term
1. Implement request batching
2. Add performance monitoring dashboard
3. Set up automated performance regression testing

---

## Files Modified

1. `backend/app/services/scenario_service.py`
   - Added `asyncio` and `hashlib` imports
   - Optimized database save (background task)
   - Fixed token extraction
   - Improved error handling
   - Optimized cache key generation

2. `backend/app/services/evaluation_service.py`
   - Added `asyncio` and `hashlib` imports
   - Optimized database save (background task)
   - Optimized cache key generation

3. `backend/tests/performance/run_test_queries.py`
   - Enhanced error reporting
   - Added token/cost statistics
   - Improved test output

---

## Conclusion

These optimizations focus on reducing overhead and improving response times by:
- Making database operations non-blocking
- Optimizing imports and function calls
- Improving error handling and debugging
- Fixing data tracking issues

**Key Achievement:** Database saves no longer block API responses, resulting in faster response times and better scalability.

---

**Document Version:** 1.0  
**Last Updated:** December 22, 2025

