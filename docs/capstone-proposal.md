# Capstone Proposal

**Course:** Building AI-Powered Applications
**Team Name:** Ascend.AI
**Project Title:** TripMind – AI Travel Route Planner
**Date:** 10/14/2025

---

## 1. Problem Statement

### The Problem

Travelers often plan road trips using map apps that only optimize **time and distance**, overlooking meaningful stops along the way. Many miss hidden attractions, local landmarks, and scenic detours simply because such recommendations require manual searching or prior local knowledge.

Existing map apps (like Google Maps) show points of interest only when manually searched and lack personalized AI logic for trip enrichment. Our system aims to solve this by recommending **relevant sightseeing locations** dynamically based on user input, travel route, and distance constraints.

---

### Scope

**In Scope:**

* Route input (start, destination, max distance)
* AI-based suggestion and ranking of nearby places
* Integration with map visualization
* Basic user authentication and trip saving

**Out of Scope (Future Work):**

* Real-time traffic or weather prediction
* Social trip sharing
* Advanced personalization based on user profiles

**Why This Scope Makes Sense:**
It’s technically achievable in one semester, demonstrates AI reasoning and data integration, and delivers tangible value for travelers.

---

## 2. Target Users

**Primary Users:**
Independent travelers, students, and families who enjoy road trips or exploring new areas.

**User Needs:**

1. Discover interesting places along their route without manual search.
2. Save and view planned trips conveniently.
3. Receive ranked recommendations matching interests (e.g., history, food, nature).

**Pain Points:**

* Manual map searches are tedious.
* No intelligent “route companion” exists.
* Limited AI filtering in current travel apps.

---

## 3. Success Criteria

### Product Success Metrics

1. ≥80% of test users find recommendations relevant.
2. App responds within 5 seconds after submission.
3. Successful save/load for at least 3 user trips.
4. ≥90% uptime of deployed MVP during testing.

### Learning Goals

* **Sopo:** Project management, documentation.
* **Toma:** API design, PostgreSQL integration.
* **Davit:** AI model integration (Gemini API) & backend optimization.
* **Temuri:** Frontend state management, map UX.

---

## 4. Technical Architecture

**System Overview:**
Users enter their route (start + end + max distance). The frontend sends these to the FastAPI backend, which calculates the main route and queries nearby attractions via external APIs (Google Maps, OpenTripMap).
AI filtering using **Gemini API** ranks results by relevance (category, popularity, diversity) before returning recommendations to the frontend for visualization.

**Technology Stack:**

* **Frontend:** React + Tailwind + PostgreSQL Auth
* **Backend:** Python + FastAPI
* **AI Service:** Google Gemini API for ranking/filtering
* **Database:**  PostgreSQL
* **Hosting:** Render / Vercel

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

## 5. Risk Assessment

| Risk                        | Likelihood | Impact | Mitigation                                    |
| --------------------------- | ---------- | ------ | --------------------------------------------- |
| API cost or rate limits     | Medium     | Medium | Cache results & use free tiers efficiently    |
| Low AI accuracy in ranking  | Medium     | High   | Fine-tune prompts and verify outputs manually |
| Map API integration failure | Low        | High   | Backup with OpenTripMap                       |
| Workload imbalance          | Medium     | Medium | Weekly check-ins and reassignment             |

---

## 6. Research Plan

**Technical Questions:**

1. How to combine route geometry with distance filtering?
2. Which Gemini model provides the best ranking cost-performance?
3. How to handle large map data efficiently?

**Proof of Concept (Weeks 3–4):**

* Basic API connection
* Return nearby places within set radius
* AI ranks them by type (sightseeing, nature, etc.)

---

## 7. User Study Plan

* **Participants:** 5–8 students/travelers
* **Goal:** Test if AI suggestions feel relevant and useful.
* **Metrics:** Relevance rating, time to complete a plan, satisfaction score.

---

## 8. Timeline (Simplified)

| Week | Focus    | Deliverables              |
| ---- | -------- | ------------------------- |
| 1    | Setup    | Repo + team contract      |
| 2    | Research | API testing & route logic |
| 3    | Backend  | Route endpoint            |
| 4    | AI       | Gemini ranking logic      |
| 5    | Frontend | Map + connection          |
| 6    | Auth     | PostgreSQL integration      |
| 7    | Testing  | User flow validation      |
| 8–10 | MVP      | Deploy + presentation     |

---

## 9. Budget

| Item       | Est. Cost                   |
| ---------- | --------------------------- |
| Gemini API | Free                        |
| Map APIs   | Free                        |
| Hosting    | Free (Render/Vercel)        |
| **Total**  | **Free**                    |

---

## 10. References

* Google Maps Platform Docs
* OpenTripMap API Docs
* Gemini API Documentation
* PostgreSQL Documentation

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
