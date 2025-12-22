# Capstone Link - Lab 9

**Team Name:** Ascend.AI  
**Project Title:** CareerSim Platform  
**Team Members:** Sopo Mrelashvili, Toma Danelia, Davit Ioramashvili, Temuri Machavariani  
**Date:** December 22, 2025  
**Repository:** https://github.com/dioramashvili/Ascend.AI  

---

## Capstone Integration Summary

This document explains how Lab 9 performance testing integrates into the full Capstone project and supports the evaluation plan.

---

## Performance Baseline Integration

### Purpose
Lab 9 establishes a performance baseline that directly supports the **Technical Success Metrics** defined in our Capstone Proposal:

| Metric | Target (Week 15) | Lab 9 Baseline | Status |
|--------|------------------|----------------|--------|
| **AI Accuracy** | >85% | N/A (quality testing) | ⏳ |
| **Latency** | <3s | 7.846s | ❌ |
| **Cost/session** | <$0.50 | $0.00* | ⏳ |
| **DB uptime** | >99% | N/A | ⏳ |

*Token tracking fixed, will be measured in next run

### Integration Points

1. **Evaluation Plan Support**
   - Lab 9 metrics feed into `docs/week-4/evaluation-plan-v2.md`
   - Performance baseline used for Week 4-15 tracking
   - Supports "Technical Metrics (System Performance)" section

2. **Capstone Proposal Metrics**
   - Directly measures targets from `docs/week-4/capstone-proposal-v2.md` Section 3
   - Provides baseline for "Technical Success Metrics" table
   - Informs cost model validation

3. **Architecture Validation**
   - Performance results validate architecture decisions
   - Identifies bottlenecks in current implementation
   - Supports `docs/week-4/architecture-v2.md` performance claims

---

## Test Infrastructure Reuse

### Components Used Across Capstone

1. **Test Script** (`backend/tests/performance/run_test_queries.py`)
   - Reusable for ongoing performance monitoring
   - Can be extended for load testing
   - Integrates with CI/CD pipeline (future)

2. **Metrics Collection**
   - Token tracking supports cost analysis
   - Latency metrics support UX optimization
   - Success rate tracking supports reliability goals

3. **Error Analysis**
   - Identifies system weaknesses
   - Guides improvement priorities
   - Supports reliability targets

---

## Next Steps for Capstone

### Week 9-10: Performance Optimization
- Address Lab 9 identified issues
- Re-run baseline tests
- Optimize latency to meet <3s target

### Week 11-12: Load Testing
- Extend test script for concurrent requests
- Measure system behavior under load
- Validate scalability assumptions

### Week 13-15: Production Monitoring
- Deploy performance monitoring dashboard
- Track metrics continuously
- Compare to Lab 9 baseline

---

## Related Capstone Documents

- **Capstone Proposal:** `docs/week-4/capstone-proposal-v2.md`
  - Section 3: Success Criteria (Technical Metrics)
  - Section 7: Cost Calculation
  
- **Evaluation Plan:** `docs/week-4/evaluation-plan-v2.md`
  - Section 1: Success Metrics Framework
  - Section 6: Performance Evaluation

- **Architecture:** `docs/week-4/architecture-v2.md`
  - Performance characteristics
  - System design decisions

---

## Improvement Plan

Based on Lab 9 results, the following improvements are planned:

1. **Immediate (Week 9)**
   - Fix career validation issues
   - Re-run baseline tests
   - Verify token tracking

2. **Short-term (Week 10-11)**
   - Optimize latency (target: <3s)
   - Implement caching strategies
   - Add error recovery mechanisms

3. **Long-term (Week 12-15)**
   - Set up automated performance monitoring
   - Integrate tests into CI/CD
   - Track performance trends

---

## Conclusion

Lab 9 performance baseline provides critical data for:
- Validating technical success metrics
- Identifying optimization opportunities
- Supporting evaluation plan execution
- Informing architecture decisions

The test infrastructure created in Lab 9 will be reused throughout the capstone project for continuous performance monitoring and validation.

---

**Last Updated:** December 22, 2025

