# Comprehensive Evaluation Plan (Version 2)

**Project Name:** Ascend AI  
**Team Members:** Sopo Mrelashvili, Toma Danelia, Davit Ioramashvili, Temuri Machavariani  
**Date:** Week 4, October 28, 2025  
**Version:** 2.0

---

## 📋 Executive Summary

**Evaluation Philosophy:**  
We aim to measure success by validating AI accuracy, user experience, and system reliability through a structured testing and monitoring plan across Weeks 4–15.

**Key Metrics:**  
1. Task Completion Rate >70%  
2. Response Latency <3s  
3. AI Accuracy >85%  
4. User Satisfaction >4.0/5.0  
5. Would Recommend >60%  

**Timeline:** Week 4 through Week 15 evaluation activities

---

## 1. Success Metrics Framework

### Product Metrics (User Experience)

| Metric | Target (Week 15) | How Measured | Why This Matters |
|--------|------------------|--------------|------------------|
| **Task Completion Rate** | >70% | User testing: % completing core workflow without assistance | Validates usability |
| **Time to Complete Core Task** | <3 min | Timed tasks during user testing | Efficiency indicator |
| **Error Rate** | <10% | Count of errors per session | UX reliability |
| **User Satisfaction** | >4.0/5.0 | Post-task survey (SUS + custom) | Overall experience |
| **Would Recommend (NPS-style)** | >60% | Yes/No survey question | Product-market fit |
| **Feature Discovery Rate** | >80% | % of users finding key features | Validates UI clarity |

### Technical Metrics (System Performance)

| Metric | Target | How Measured | Why This Matters |
|--------|--------|--------------|------------------|
| **AI Accuracy** | >85% | Golden set (50+ test cases) | Core value validation |
| **Precision** | >90% | TP / (TP + FP) | Reduce false positives |
| **Recall** | >80% | TP / (TP + FN) | Capture all relevant outputs |
| **Response Latency (P95)** | <3s | Backend logs | UX threshold |
| **API Uptime** | >99% | Monitoring dashboards | Reliability |
| **Cost per Query** | <$0.05 | Cost logs | Economic viability |
| **Token Usage per Query** | <1000 tokens | API logging | Cost optimization |

### Safety Metrics (Responsible AI)

| Metric | Target | How Measured | Why This Matters |
|--------|--------|--------------|------------------|
| **Content Filter Pass Rate** | >95% | % harmful prompts blocked | Safety compliance |
| **Bias Score** | <1.2x disparity | Demographic parity ratio | Fairness |
| **PII Leakage Rate** | 0% | Audit logs | Privacy requirement |
| **Hallucination Rate** | <5% | Manual review | Trustworthiness |
| **Red Team Pass Rate** | >90% | Adversarial testing | Security check |

---

## 2. Golden Set Design

### Overview

**Definition:** Standardized set of 50+ test cases covering typical, edge, and adversarial scenarios.  

**Purpose:** Measure AI accuracy objectively, regression testing, and validate improvements.

**Composition:**  
- Typical: 70% (35 cases)  
- Edge: 20% (10 cases)  
- Adversarial/Safety: 10% (5 cases)  

### Typical Use Cases (35 cases)

| Test ID | Input | Expected Output | Acceptance Criteria |
|---------|-------|-----------------|---------------------|
| T001 | [Description] | [Expected result] | - [ ] Criterion 1<br>- [ ] Criterion 2 |
| T002 | [Description] | [Expected result] | - [ ] Criterion 1<br>- [ ] Criterion 2 |

### Edge Cases (10 cases)

| Test ID | Input | Expected Behavior | Why Testing This |
|---------|-------|-----------------|-----------------|
| E001 | Faded receipt | Extracts if possible, low confidence flagged | Real-world scenario |
| E002 | Foreign language receipt | Extract numbers, attempt translation | Global users |
| E003 | Crumpled receipt | Attempt extraction | Handling user mishandling |

### Adversarial/Safety Cases (5 cases)

| Test ID | Input | Expected Behavior | Why Testing This |
|---------|-------|-----------------|-----------------|
| A001 | Blank image | Returns error: "No receipt detected" | Prevent hallucination |
| A002 | Credit card image | Reject | PII protection |
| A003 | Prompt injection attempt | Ignores injection | Security |

---

## 3. Evaluation Timeline

| Week | Activity | Metric | Target |
|------|----------|-------|--------|
| 4 | Baseline measurement | Initial accuracy | Document current state |
| 6 | Golden set creation | Test coverage | 50+ cases |
| 7 | User testing round 1 | Task completion | >70% |
| 11 | Safety audit | Red team pass rate | >90% |
| 14 | User testing round 2 | Satisfaction | >4.0/5.0 |
| 15 | Final evaluation | All metrics | Hit all targets |

---

## 4. User Testing Protocols

### Round 1: Week 7

**Objective:** Validate core UX and AI accuracy  

**Participants:** 5 users, target audience, $25 incentive each  

**Tasks:** 3-5 core workflows with time limits and success criteria

**Data Collection:**  
- **Quantitative:** Task completion, time on task, errors, clicks  
- **Qualitative:** Think-aloud, facial expressions, spontaneous comments, post-task survey  

**Survey Example Questions:**  
1. Ease of use (1-5)  
2. Accuracy perception (1-5)  
3. Trust AI output (1-5)  
4. Regular usage likelihood (1-5)  
5. Recommend to friend? (Y/N)  
6. Open feedback: love, frustrations, missing features, willingness to pay  

### Round 2: Week 14

- New participants  
- Updated tasks based on Round 1 improvements  
- Higher targets (>85% completion, >4.5/5 satisfaction)

---

## 5. Automated Testing Strategy

- **Unit Tests (80%)**: isolated functions, >80% coverage  
- **Integration Tests (15%)**: API + database interactions  
- **E2E Tests (5%)**: full user journeys, Playwright or Cypress  

**Implementation:**  
- Week 6: setup frameworks, write first unit tests, CI/CD pipeline  
- Week 8: integration tests  
- Week 10: E2E tests  

---

## 6. Performance Evaluation

- Latency testing with k6/Locust  
- Concurrent users: 10, 50, 100  
- Targets: P50 <2s, P95 <3s, P99 <5s  

```python
# k6 example
import http from 'k6/http';
import { check } from 'k6';
export default function() {
    let res = http.post('https://api.example.com/upload', { /* data */ });
    check(res, {'status 200': (r) => r.status === 200, 'latency <3s': (r) => r.timings.duration < 3000 });
}
