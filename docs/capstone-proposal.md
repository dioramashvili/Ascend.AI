# Capstone Proposal

**Course:** Building AI-Powered Applications  
**Team Name:** Ascend.AI  
**Project Title:** CareerSim – AI Career Experience Simulator  
**Date:** 10/26/2025  

---

## 1. Problem Statement

### The Problem

Choosing a career path is one of the most impactful decisions in life — yet most people make it without experiencing what the job actually feels like. Students and early-career individuals often rely on limited information, assumptions, or external advice. As a result, they invest years studying or working in fields that don’t align with their interests, skills, or expectations.

Currently, the only way to “test” a career is through internships or shadowing programs, which are difficult to access, short-term, and not scalable. There’s no immersive, low-cost way to simulate a real-world professional environment before committing to it.

An AI-powered system can bridge this gap by **simulating authentic workplace experiences** through dynamic, scenario-based interactions and performance assessments — helping users explore, experience, and evaluate careers before pursuing them.

---

### Scope

**What's In Scope:**
- AI-generated real-world career scenarios (via Gemini API)  
- User interaction with simulations and decision-making tasks  
- AI-based feedback and assessment of user responses  
- Basic user registration and progress tracking  

**What's Out of Scope (Future Work):**
- Integration with educational or recruitment systems  
- Long-term behavioral analytics

**Why This Scope Makes Sense:**  
It’s feasible within a semester and demonstrates strong AI integration through text generation, evaluation, and interaction loops.

---

## 2. Target Users

### Primary User Persona

**User Type:** Students, job seekers, and early-career professionals  

**Demographics:**
- Age range: 16–30  
- Technical proficiency: Basic (comfortable using web platforms)  
- Context of use: Desktop or mobile browser  

**User Needs:**
1. **Career Exploration:** Understand what daily work in a specific field is like.  
2. **Skill Assessment:** Receive feedback on their choices and reasoning.  
3. **Guidance:** Discover career paths that align with personal strengths.  

**User Pain Points:**
- Limited exposure to real job challenges.  
- Career decisions often made based on stereotypes or advice.  
- Lack of personalized feedback on suitability for different roles.

---

## 3. Success Criteria

### Product Success Metrics

1. **Relevance:** 80% of users agree that scenarios feel realistic.  
2. **Engagement:** 70% of users complete at least one full simulation.  
3. **Accuracy:** AI assessment aligns with expert human feedback ≥75%.  
4. **Satisfaction:** Average user rating ≥4/5 in feedback survey.  
5. **Performance:** Response time under 5 seconds per prompt.  

### Technical Success Criteria

- Average API latency: <3 seconds  
- Backend uptime: ≥95% during testing  
- Scenario generation cost: <$0.15 per session  
- Error rate: <5%  

### Learning Goals

- **Sopo:** Team coordination, user testing, and documentation.  
- **Toma:** Backend architecture, database management.  
- **Davit:** AI integration with Gemini API, prompt design, and scoring logic.  
- **Temuri:** Frontend UI/UX design and scenario interaction flow.

---

## 4. Technical Architecture

### System Overview

Users select a career (e.g., Software Engineer, Nurse, Project Manager).  
The frontend collects their input and sends it to the backend, which uses the **Gemini API** to generate realistic workplace scenarios and decisions the user must make.  
Once the user interacts with the simulation, Gemini analyzes their choices and provides qualitative and quantitative assessments.

Results are stored in a **PostgreSQL database**, allowing users to view their career readiness and track progress across multiple simulations.

---

### Architecture Diagram


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



---

### Technology Stack

**Frontend:**
- React + TailwindCSS  
- Deployed via Vercel  

**Backend:**
- FastAPI (Python)  
- Hosted on Render or Railway  

**AI/ML Services:**
- Gemini API for dynamic scenario generation and response evaluation  

**Database:**
- PostgreSQL (Render or Neon hosting)  

**Tooling & DevOps:**
- GitHub for version control  
- GitHub Projects for task management  

---

## 5. Risk Assessment

### Technical Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-------------|---------|-------------|
| Gemini API rate limits | Medium | Medium | Cache previous scenarios; stagger requests |
| Poor scenario realism | Medium | High | Manual review and prompt iteration |
| Assessment inaccuracy | Low | High | Multi-prompt evaluation; human benchmark tests |
| Data loss | Low | High | Regular DB backups and error handling |

### Product Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-------------|---------|-------------|
| Low user engagement | Medium | High | Add gamification and progress tracking |
| Overly complex simulations | Medium | Medium | Start with simple, text-based scenarios |
| Scope creep | Medium | Medium | Weekly milestone check-ins and strict scope control |

---

## 6. Research Plan

**Technical Questions:**
1. How to design effective prompt structures for realistic AI simulations?  
2. How to quantify qualitative feedback from Gemini?  
3. How to measure user engagement and perceived realism effectively?  

**Proof of Concept (Weeks 3–4):**
- Simple “day in the life” simulation generated by Gemini  
- User inputs and responses logged  
- AI returns narrative feedback  

---

## 7. User Study Plan

**Participants:** 5–10 university students exploring career choices  
**Goal:** Evaluate how realistic and helpful the simulation feels  
**Metrics:**  
- Perceived realism (1–5 scale)  
- Usefulness for career choice decisions  
- Likelihood to recommend  

**Recruitment:**  
University student groups and social media channels  

---

## 8. Timeline

| Week | Focus | Deliverables |
|------|--------|--------------|
| 1 | Setup | Repo, environment, team contract |
| 2 | Research | Prompt design & Gemini integration |
| 3 | Backend | Scenario generation endpoint |
| 4 | Frontend | User input and response display |
| 5 | AI | Assessment logic implementation |
| 6 | DB | PostgreSQL connection & user data |
| 7 | Testing | Internal simulation testing |
| 8–10 | MVP | Full deployment and feedback round |

---

## 9. Budget

| Item | Est. Cost |
|------|------------|
| Gemini API | Free |
| Hosting (Render/Vercel) | Free Tier |
| PostgreSQL Hosting | Free Tier (Neon/Render) |
| **Total** | **Free** |

---

## 10. References
- Google Gemini API Documentation  
- FastAPI Framework Docs  
- PostgreSQL Official Docs  
- React + TailwindCSS Documentation  

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
