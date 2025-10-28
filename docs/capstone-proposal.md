# Refined Capstone Proposal (Version 2)

**Project Name:** CareerSim – AI Career Experience Simulator  
**Team Members:** Sopo, Toma, Davit, Temuri  
**Date:** Week 4, October 27, 2025  
**Version:** 2.0 (Updated from Week 2 submission)

---

## 📋 Document Change Log

### What Changed Since Week 2?

| Section | Change Type | Summary |
|----------|-------------|----------|
| Problem Statement | **Refined** | Narrowed problem focus on career misalignment due to lack of experiential feedback |
| Target Users | **Expanded** | Added personas for students and early-career professionals |
| Success Criteria | **Enhanced** | Introduced measurable product and AI metrics |
| Technical Architecture | **Updated** | Clarified data flow and architecture diagram |
| Risk Assessment | **Expanded** | Added bias, privacy, and hallucination risks |
| Responsible AI | **New** | Added as required course section |
| Prompt Engineering | **New** | Detailed prompt examples for generation and evaluation |
| Timeline | **Refined** | Aligned milestones with MVP delivery plan |

---

## 1. Problem Statement (Updated)

### The Problem

**Original (Week 2):**
> People struggle to choose careers that align with their skills and interests, often realizing the mismatch too late.

**Refined (Week 4):**

Selecting a career path remains a high-stakes, low-feedback decision. Most students and early-career professionals choose their direction without ever “experiencing” the job. This leads to dissatisfaction, wasted education costs, and high career-switching rates.

Interviews with 7 university students and 3 career coaches revealed that nearly all participants lacked practical ways to explore multiple fields before committing. Traditional internships are limited, unpaid, or inaccessible. Online career quizzes provide generic suggestions and lack real-life context.

**CareerSim** addresses this by providing realistic, AI-generated career simulations where users engage with real-world decision scenarios and receive personalized feedback based on their responses. Through this, users gain experiential insights and can make better-informed career decisions.

**Why AI?**  
AI enables dynamic scenario generation, role-based reasoning, and instant evaluation — creating personalized, cost-effective simulations that mimic the diversity of real professional situations.

---

## 2. Target Users (Updated)

### User Personas

**Primary User: Nino the University Student**  
- **Demographics:** 21 years old, lives in Tbilisi, studies business administration  
- **Goals:** Explore different career paths before graduation  
- **Pain Points:** Limited access to internships, overwhelmed by online advice  
- **Behaviors:** Uses LinkedIn Learning, reads job reviews online, but lacks direct experience  
- **Success Metrics:** Feels confident choosing a career after 3–4 simulations  

**Secondary User: Giorgi the Career Switcher**  
- **Demographics:** 29 years old, working in customer support, considering UX design  
- **Goals:** Understand if design work matches his skills  
- **Pain Points:** Afraid of investing in wrong courses or bootcamps  
- **Behaviors:** Takes online tutorials but lacks practical application feedback  
- **Success Metrics:** Receives clear AI feedback about fit for design career  

### User Validation

**How We Validated:**
- ✅ Interviewed 10 target users (students + professionals)
- ✅ Analyzed forums (Reddit, LinkedIn) on career uncertainty
- ✅ Collected feedback from 2 career advisors

**Key Insights:**
1. Users want a “test drive” for careers without long-term commitments.  
2. Personalized feedback increases trust and engagement.  
3. AI explanations must be clear and human-like to maintain motivation.  

---

## 3. Success Criteria (Updated & Measurable)

### Product Success Metrics

| Metric | Target (Week 15) | Measurement | Baseline (Week 4) |
|--------|------------------|--------------|------------------|
| Simulation completion rate | ≥70% | System logs | Not measured |
| Realism rating | ≥80% “realistic” | Post-session survey | Not measured |
| Feedback clarity | ≥4.0/5.0 | Likert survey | Not measured |
| AI feedback agreement with human | ≥75% | Expert review comparison | Prototype |
| User trust | ≥60% “would recommend” | End survey | Not measured |

### Technical Success Metrics

| Metric | Target | Method | Current |
|--------|---------|---------|---------|
| AI Accuracy | >85% | Golden test set | 75% |
| Latency | <3s | Backend logs | 4.5s |
| Cost/session | <$0.50 | Token logs | ~$0.46 |
| DB uptime | >99% | Health checks | N/A |
| Prompt stability | <5% variance | Automated prompt test | Planned |

### Learning Goals (Team-Level)

| Team Member | Learning Goal | Success Criteria | Progress |
|-------------|---------------|------------------|-----------|
| **Sopo** | Improve project management & coordination | Weekly meetings on time; updated backlog | ✅ On track |
| **Toma** | Build production-grade backend (FastAPI + PostgreSQL) | Deployed with >99% uptime | ⚙️ In progress |
| **Davit** | Master Gemini API integration | Stable prompt logic; <5% hallucination rate | ⚙️ In progress |
| **Temuri** | Design user-friendly frontend | Realistic scenario interaction UX | ⚙️ In progress |

---

## 4. Technical Architecture (Updated)

### Architecture Evolution

| Component | Week 2 | Week 4 | Reason |
|------------|--------|--------|--------|
| **Frontend** | Basic React | React + Vite (optimized) | Faster build and modular UI |
| **Backend** | Flask | FastAPI | Needed async for Gemini |
| **Database** | Supabase | PostgreSQL | Chosen for reliability |
| **AI Model** | OpenAI GPT | Gemini Pro + Flash | Better latency-cost balance |

### Current Architecture Diagram

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

> **Note:** Map API represents learning path visualizations showing career progress routes.

---

## 5. Responsible AI Strategy (Required)

### 5.1 Preventing Hallucinations
- Use **Gemini Pro** for evaluation, with low temperature (≤0.4).  
- Cross-verify AI content against curated job databases (e.g., O*NET).  
- Implement rule-based filters to detect made-up roles or companies.

### 5.2 Content Moderation
- Apply Gemini’s built-in **SafetySettings** for hate, self-harm, and NSFW content.  
- Sanitize all user input with regex and Google Perspective API.  

### 5.3 Data Privacy
- No personal data stored; only session IDs and response logs.  
- Use encrypted connections (TLS) and environment-based key storage.  
- Users can request data deletion anytime.  

### 5.4 Bias & Fairness
- Regularly test across gender, race, and cultural references.  
- Include bias-check prompts (“Does this assume gender or culture?”).  

### 5.5 Disclaimers
> ⚠️ **Disclaimer:** All simulations are AI-generated and for educational purposes only. CareerSim does not provide certified career counseling or professional advice.

---

## 6. Prompt Engineering Strategy (New)

### Scenario Generation Prompt

You are a simulation designer for realistic job experiences.
Generate a scenario (200–300 words) for {career_title}.
Include one realistic challenge and 3 options (A/B/C).
Avoid hallucinations and unrealistic data.
Return JSON: {"scenario": "...", "options": ["A", "B", "C"]}.


### Evaluation Prompt
You are a professional in {career_title}.
Evaluate the user’s choice {user_answer} in the scenario below.
Give reasoning and assign score (0–10).
Return JSON: {"feedback": "...", "score": number}.



### Model Choice
- **Gemini Flash:** Quick generation for scenarios.  
- **Gemini Pro:** Deeper reasoning for evaluations.  
- Prompt templates versioned for reproducibility.  

---

## 7. Cost Calculation (Detailed)

| Stage | Model | Avg Tokens | Cost per 1K tokens | Requests/session | Total |
|--------|--------|-------------|--------------------|------------------|--------|
| Scenario Generation | Gemini Flash | 700 | $0.0003 | 1 | $0.21 |
| Evaluation | Gemini Pro | 500 | $0.0025 | 2 | $0.25 |
| **Total Estimated** | — | — | — | — | **≈ $0.46 per session** |

**Optimization:**  
Batch evaluations + caching repeated prompts = up to 35% cost reduction.

---

## 8. Risk Assessment (Expanded)

| Risk | Likelihood | Impact | Severity | Mitigation |
|------|-------------|---------|-----------|-------------|
| AI hallucination | Medium | High | 🔴 | Fact-checking filters + low temperature |
| Prompt injection | Medium | High | 🔴 | Input sanitization + schema validation |
| Career bias | Medium | High | 🟡 | Bias testing, audits |
| Privacy breach | Low | High | 🟡 | Data encryption, anonymization |
| API failure | Medium | Medium | 🟡 | Retry logic + fallback responses |
| Cost overrun | Low | Medium | 🟢 | Token monitoring, usage limits |

---

## 9. User Study Plan (Updated)

**Participants:** 10 students and early-career professionals  
**Metrics:**
- Realism (Likert 1–5)  
- Usefulness for career choice  
- Clarity of AI feedback  
- Fairness & trust perception  

**Plan:**  
- Week 7: Run 10 simulation tests  
- Week 8: Analyze feedback & revise prompts  
- Week 10: Run follow-up tests for validation  

---

## 10. Project Timeline (Realistic)

| Week | Focus | Deliverables | Status |
|------|--------|--------------|--------|
| 1 | Setup | Repo + contract | ✅ |
| 2 | Prompt R&D | Early Gemini tests | ⚙️ In progress |
| 3 | Backend | FastAPI + DB structure | ⏳ Planned |
| 4 | Frontend | Simulation UI | ⏳ Planned |
| 5 | AI Evaluation | Scoring system | ⏳ Planned |
| 6 | Responsible AI | Moderation, bias tests | ⏳ Planned |
| 7 | Testing | 1st user feedback round | ⏳ Planned |
| 8–10 | MVP | Deployment + validation | ⏳ Planned |

---

## 11. Budget

| Item | Est. Cost | Notes |
|------|------------|-------|
| Gemini API | $40 | Free tier + course credit |
| Hosting | Free | Vercel / Render |
| Database | Free | Neon / PostgreSQL |
| **Total** | **≈ $40** | Shared among team |

---

## 12. Team Contract Summary

Our team meets twice weekly (Wed 8 PM, Sun 6 PM).  
Each member owns a major project area:  
Sopo – PM/docs, Toma – backend, Davit – AI integration, Temuri – frontend.  
Conflicts are resolved collaboratively within 48 hours, otherwise escalated to instructor.  
See [docs/team-contract.md](./team-contract.md) for full details.

---

## 13. Contingency & Ethical Considerations

- Backup models: **OpenAI GPT-4o-mini** or **Claude Haiku**.  
- Manual review required before new scenarios are released.  
- Fallback mode if Gemini API unavailable.  

---

## 14. Technical Decisions Log

| Decision Area | Option A | Option B | Chosen | Rationale |
|----------------|-----------|-----------|----------|------------|
| Backend Framework | Flask | **FastAPI** | ✅ | Async support, auto-docs, better with Gemini API. |
| AI Provider | OpenAI GPT | **Gemini Pro + Flash** | ✅ | Lower cost, stronger JSON formatting, integrated moderation. |
| Database | Supabase | **PostgreSQL (Neon)** | ✅ | Simpler control, better performance. |
| Hosting | AWS Lambda | **Render / Vercel** | ✅ | Zero-config, free tier. |
| Frontend | React CRA | **React + Vite** | ✅ | Faster build, modular structure. |

---

## 15. Open Questions

1. How to quantify **AI realism** beyond subjective surveys?  
2. Can Gemini provide consistent JSON outputs under load?  
3. Should we include **audio-based scenarios** in Phase 2?  
4. How to gamify progress without trivializing serious careers?  
5. What is the best method to store **AI prompt versions** for reproducibility?

---

## 16. Revision History

| Date | Change | Author |
|------|---------|--------|
| 2025-10-27 | Major revision aligned to Refined Template | Ascend.AI Team |
| 2025-10-28 | Added Week 3-4 Learnings, Technical Decisions Log, and Open Questions | Davit Ioramashvili |

---

**Document Version:** 2.0  
**Next Review:** Week 7 (after user testing)
