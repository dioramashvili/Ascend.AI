# Capstone Proposal

**Course:** Building AI-Powered Applications  
**Team Name:** Ascend.AI  
**Project Title:** CareerSim – AI Career Experience Simulator  
**Date:** 10/26/2025  

---

## 1. Problem Statement

Choosing a career path is one of the most impactful life decisions, yet most people make it without experiencing what the job is actually like. Students and early-career professionals often rely on stereotypes, online articles, or hearsay instead of real-world exposure. As a result, many waste years pursuing unsuitable fields.

Traditional options (internships, shadowing) are limited, costly, and hard to access.  
**CareerSim** solves this by using AI to simulate realistic workplace scenarios, letting users “test-drive” careers through interactive decision-making experiences and AI-driven performance assessments.

---

### Scope

**In Scope**
- AI-generated text scenarios simulating professional tasks  
- User decision-making and reflective feedback loop  
- AI assessment of responses (qualitative + numeric scoring)  
- Secure user accounts and progress tracking  

**Out of Scope (Future Work)**
- VR or multimedia simulation  
- Integration with recruiters or institutions  
- Long-term skill-tracking analytics  

---

## 2. Target Users

**Primary Users:**  
High-school students, university students, and early-career switchers.

**User Needs**
1. Realistic, low-barrier exposure to multiple careers.  
2. Actionable feedback about fit and performance.  
3. Safe experimentation environment with AI guidance.  

**Pain Points**
- Lack of accessible “try-before-you-commit” career experiences.  
- Overwhelm from information and contradictory advice.  
- No objective feedback mechanism about skill-role alignment.

---

## 3. Success Criteria

### Product Success
- ≥80 % users rate simulations as “realistic” or “very realistic”.  
- ≥70 % complete at least one full simulation session.  
- ≥75 % alignment between AI and expert human evaluation.  
- Average latency < 5 s per AI call.  

### Learning Goals
- **Sopo:** Coordination, research documentation.  
- **Toma:** Backend and database design.  
- **Davit:** Gemini API integration and prompt design.  
- **Temuri:** Frontend UX and scenario visualization.

---

## 4. Technical Architecture

Users choose a career track → system generates a simulation → user interacts and responds → Gemini evaluates and scores → data stored in PostgreSQL.


```
┌─────────────┐      ┌──────────────────┐       ┌─────────────┐
│   User      │─────▶│   Frontend      │─────▶│   Backend    │
│  (Browser)  │      │   (React)        │◀─────│  (FastAPI)  │
└─────────────┘      └──────────────────┘       └─────────────┘
                                                     │
                                        ┌────────────┼────────────┐
                                        ▼            ▼            ▼
                                 ┌──────────┐ ┌──────────┐ ┌──────────┐
                                 │ Gemini   │ │ Map API  │ │PostgreSQL│
                                 │   API    │ │ (Routes) │ │   DB     │
                                 └──────────┘ └──────────┘ └──────────┘
```




> **Note:** “Map API (Routes)” here refers to a learning-path mapping utility (not geographic maps). It visualizes a user’s simulation journey across multiple career options.

---

## 5. Responsible AI Strategy

### 5.1 Preventing Hallucinations
- Use **Gemini 1.5 Pro** for reasoning reliability; validate generated content against curated datasets describing real job responsibilities.  
- Restrict prompt temperature (≤ 0.4) and require factual grounding through “context inserts” (verified career data).  
- Add a verification layer: outputs pass through rule-based filters to check for invented company names or tasks.

### 5.2 Content Moderation
- Employ Gemini’s **SafetySettings** for toxicity, self-harm, and sexual content filters.  
- Sanitize user inputs using regex + Google Perspective API to prevent prompt injection or inappropriate content.

### 5.3 Data Privacy
- Store only anonymized session IDs and responses (no personal data).  
- Encrypt all data at rest and in transit (PostgreSQL TLS, HTTPS).  
- Users can delete their data at any time via profile settings.

### 5.4 Bias Testing
- Test scenario balance across gender, region, and career stereotypes.  
- Implement bias-detection prompts (“Does this scenario assume gender or culture?”).  
- Perform manual audits on 10 % of outputs per release.

### 5.5 Disclaimers
Displayed on every page:
> ⚠️ **AI-Generated Simulation** – CareerSim provides educational insights only. It does **not** constitute certified career counseling or professional advice.

---

## 6. Prompt Engineering Strategy

### 6.1 Scenario Generation Prompt
Example: You are a simulation designer for realistic job experiences.
Generate a short, role-specific scenario (200–300 words) for a {career_title}.
Include a realistic problem, 3 decision options (A/B/C), and clear context.
Avoid hallucinating company names or statistics. Output JSON with keys:
{"scenario": "...", "options": ["A", "B", "C"]}


### 6.2 Response Evaluation Prompt
Example: You are an experienced professional in {career_title}.
Evaluate the user's choice {user_answer} from the scenario below.
Explain reasoning and assign a numeric score (0–10) for decision quality.
Return JSON: {"feedback": "...", "score": number}


### 6.3 Model Choice
- **Gemini 1.5 Pro** for evaluation (accuracy > reasoning speed).  
- **Gemini 1.5 Flash** for scenario generation (fast, low-cost).  
- Prompt templates stored in backend; versioned for traceability.

---

## 7. Cost Calculation

| Stage | Model | Tokens/Request | Requests/Session | Cost / 1K tokens | Total / Session |
|--------|--------|----------------|------------------|------------------|----------------|
| Scenario Generation | Gemini Flash | ~700 | 1 | $0.0003 | $0.21 |
| Evaluation | Gemini Pro | ~500 | 2 | $0.0025 | $0.25 |
| **Estimated Total** |  |  |  |  | **≈ $0.46/session** |

*Optimizations:* compress JSON responses, cache repeated scenarios, and use batch evaluation for groups of users.

---

## 8. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-------------|---------|-------------|
| AI hallucination (fake info) | Medium | High | Low-temperature prompts + fact-checking filters |
| Prompt injection | Medium | High | Sanitize inputs, strict schema validation |
| Career bias/stereotypes | Medium | High | Bias testing and audits |
| Data privacy violation | Low | High | Encrypt data, anonymize logs |
| API failure/unavailability | Medium | Medium | Retry with exponential backoff + fallback text |
| Low user engagement | Medium | Medium | Add gamification & badges |
| Cost overrun | Low | Medium | Monitor token usage & limit free tier sessions |

---

## 9. Scoring & Error Handling

### AI-to-Score Conversion
- Gemini returns 0–10 score → backend averages last 3 scores per career → normalized to 0–100 scale.  
- Results stored with timestamp and scenario ID.

### Error Handling
- Retry failed API calls up to 3 times with increasing delay.  
- If all fail, display fallback message:  
  > “Simulation temporarily unavailable — please retry later.”

---

## 10. User Study Plan

**Participants:** 8–12 students and early-career users  
**Metrics:**
- Realism (Likert 1–5)  
- Usefulness for decision-making  
- Clarity of AI feedback  
- Perceived fairness/bias  

---

## 11. Timeline

| Week | Focus | Deliverables |
|------|--------|--------------|
| 1 | Setup | Repo, environment, team contract |
| 2 | Prompt R&D | Basic Gemini Flash scenario tests |
| 3 | Backend | FastAPI + PostgreSQL skeleton |
| 4 | Frontend | React interface for simulations |
| 5 | AI Evaluation | Gemini Pro scoring logic |
| 6 | Privacy & Ethics | Moderation + bias testing |
| 7 | Testing | End-to-end user flow |
| 8–10 | MVP | Deployment + feedback collection |

---

## 12. Budget

| Item | Est. Cost | Notes |
|------|------------|-------|
| Gemini API usage | $40 | Free tier + $10 credit/month |
| Hosting (FastAPI + React) | Free | Render / Vercel free tier |
| PostgreSQL DB | Free | Render / Neon free tier |
| **Total** | **≈ $40** | Split among team |

---

## 13. Team Contract Summary

Our team meets twice weekly and tracks work through GitHub Projects. Each member owns specific components: Sopo – PM/docs, Toma – backend, Davit – AI integration, Temuri – frontend UX.  
Conflicts are resolved through group discussion within 48 hours; unresolved issues escalate to the instructor.  
See [docs/team-contract.md](./team-contract.md) for full details.

---

## 14. Contingency & Ethical Considerations

If Gemini API becomes unavailable, fallback models (OpenAI GPT-4o mini or Claude Haiku) will be used temporarily.  
All simulations undergo manual review before public release to ensure ethical and factual accuracy.

---

## 15. Revision History

| Date | Change | Author |
|------|---------|--------|
| 2025-10-27 | Initial complete revision incorporating instructor feedback | Ascend.AI Team |

---

## Instructor Use Only

**Grade: _____ / 10**

| Component | Points | Feedback |
|-----------|--------|----------|
| Problem Clarity | __/2 | |
| Technical Feasibility | __/2 | |
| Success Criteria | __/1 | |
| Risk Assessment | __/1 | |
| Research & User Plan | __/1.5 | |
| Team Contract | __/1.5 | |
| Presentation Quality | __/1 | |

**Overall Feedback:**
