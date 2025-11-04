# CareerSim Product Requirements Document (PRD)
**Version:** 2.0  
**Team:** Catalyst  
**Date:** November 2025  

---

## 🧭 Table of Contents
1. Executive Summary  
2. Problem Statement  
3. Goals & Objectives  
4. Target Audience  
5. User Needs  
6. Product Scope  
7. Key Features  
8. User Stories  
9. User Flow  
10. Design & UX Principles  
11. Technical Architecture (Updated)  
12. Technical Stack (Aligned with Architecture Evolution)  
13. Implementation Plan  
14. Success Metrics  
15. Risks & Mitigation  
16. Ethical Considerations  
17. Future Enhancements  
18. References  

---

## 1. Executive Summary
CareerSim is an interactive AI-powered web platform that enables students and early-career professionals to experience realistic job simulations before committing to a career path. By combining AI-driven scenario generation and feedback, it bridges the gap between education and the workplace.  

**Evaluation Philosophy:** Success is defined by user engagement, learning outcomes, and satisfaction with realism and guidance.  
**Key Metrics:**
1. User engagement rate (time spent, return rate)  
2. Simulation completion rate  
3. Accuracy of AI feedback (based on expert comparison)  
4. User satisfaction (post-simulation rating)  
5. Learning outcome improvement  

---

## 2. Problem Statement
Many individuals make career decisions without firsthand experience, leading to poor fit, burnout, and costly pivots. Traditional exposure methods (internships, shadowing) are limited, expensive, and inaccessible.  
CareerSim solves this by simulating authentic workplace environments using AI — providing safe, scalable, and data-driven exploration.

---

## 3. Goals & Objectives
- Enable users to explore realistic job tasks through simulations.  
- Provide AI-driven personalized feedback and guidance.  
- Help users align strengths and interests with career paths.  
- Offer educators and institutions a scalable career-experience tool.  

---

## 4. Target Audience
- University students exploring majors and career options.  
- Early-career professionals considering transitions.  
- Career counselors and academic advisors.  

---

## 5. User Needs
- Realistic, interactive job experiences.  
- Constructive performance feedback.  
- Career recommendations based on skills and behavior.  
- Seamless, accessible web experience.  

---

## 6. Product Scope
CareerSim will focus on providing simulations for 3–5 popular careers during MVP (e.g., Software Engineer, UX Designer, Data Analyst).  
AI feedback, analytics, and user dashboards will be core MVP elements.

---

## 7. Key Features
1. **AI-Powered Simulations:** Users complete realistic workplace tasks.  
2. **Dynamic Feedback System:** AI evaluates responses and provides improvement tips.  
3. **Career Fit Assessment:** Algorithm matches performance with career traits.  
4. **Admin Panel:** For educators or partners to add simulation modules.  

---

## 8. User Stories
- *As a student,* I want to experience a “day in the life” of different careers so I can decide which suits me.  
- *As a job seeker,* I want feedback on how I perform in simulations so I can identify strengths and gaps.  
- *As a counselor,* I want to track students’ results and guide them accordingly.  

---

## 9. User Flow
1. User registers →  
2. Chooses a career simulation →  
3. Completes interactive scenario →  
4. AI analyzes responses →  
5. Feedback + recommendations displayed →  
6. User tracks results on dashboard.  

---

## 10. Design & UX Principles
- Realistic and professional tone.  
- Clean UI with minimal distractions.  
- Focus on interactivity and immersion.  
- Accessibility-first design (WCAG 2.1 compliance).  

---

## 11. Technical Architecture (Updated)
CareerSim adopts a **modular and scalable architecture** built around **AI-driven microservices** and **cloud-native deployment**.  
The system follows an **API-first** approach to ensure flexibility and easy future integration with new simulation types or institutions.

**Architecture Layers:**
1. **Frontend (Client Layer):**
   - Built with **React.js + TypeScript** for performance and modularity.
   - Integrates with backend via REST and WebSocket APIs.
   - Uses **Next.js** for server-side rendering and SEO benefits.

2. **Backend (Application Layer):**
   - Core API built using **Node.js (Express)** for scalability and simplicity.
   - Handles simulation logic, AI requests, authentication, and data management.
   - Implements microservices for:
     - Simulation Management
     - AI Feedback & Analysis
     - User Profiles & Analytics

3. **AI & NLP Layer:**
   - Powered by **Python FastAPI microservices**.
   - Integrates **OpenAI GPT models** and custom fine-tuned models for scenario generation and evaluation.
   - Uses a scoring model combining NLP-based semantic analysis and structured performance rubrics.

4. **Database Layer:**
   - **PostgreSQL** as the main relational database for structured data.
   - **Redis** for caching user session data and API responses.
   - **MongoDB** (optional) for storing unstructured simulation data and AI prompts.

5. **Infrastructure:**
   - Hosted on **AWS (EC2, S3, RDS)**.
   - Containerized via **Docker** for environment consistency.
   - **CI/CD pipelines** through **GitHub Actions** for automated deployment.
   - **NGINX** used as a reverse proxy and load balancer.

6. **Security & Scalability:**
   - JWT-based authentication.
   - Role-based access control.
   - Data encryption with HTTPS/TLS.
   - Scalable via AWS Auto Scaling and Docker Swarm.

---

## 12. Technical Stack (Aligned with Architecture Evolution)

| Layer | Technology | Purpose |
|-------|-------------|----------|
| **Frontend** | React.js,| Interactive UI, SSR for SEO |
| **Backend** | FastAPI | API gateway, business logic |
| **AI/NLP** | Python (FastAPI), OpenAI API, Hugging Face Transformers | Simulation generation, feedback, scoring |
| **Database** | PostgreSQL | Persistent data, unstructured storage, caching |
| **Infrastructure** | AWS EC2/S3/RDS, Docker, GitHub Actions | Cloud hosting, containerization, CI/CD |
| **Authentication** | JWT, OAuth 2.0 | Secure user management |
| **Analytics** | Google Analytics, custom metrics via PostgreSQL | Engagement and performance tracking |

---

## 13. Implementation Plan
**Phase 1 – Foundation (Weeks 1–3):**
- Set up GitHub repo, CI/CD pipeline, and Docker environment.  
- Implement authentication and database schema.  
- Build core frontend layout.  

**Phase 2 – Simulation Core (Weeks 4–6):**
- Develop simulation generation and AI response system.  
- Integrate GPT-based scenario logic.  
- Implement feedback and scoring modules.  

**Phase 3 – Dashboard & Analytics (Weeks 7–9):**
- Develop user dashboard and tracking features.  
- Integrate analytics and feedback history.  
- Conduct MVP testing with sample users.  

**Phase 4 – Finalization (Weeks 10–12):**
- Optimize performance and polish UI.  
- Conduct usability testing.  
- Prepare for beta launch.  

---

## 14. Success Metrics
- 70%+ simulation completion rate  
- ≥ 4.0/5 user satisfaction  
- < 5% system downtime  
- Increased clarity in career choice (survey-based metric)  

---

## 15. Risks & Mitigation
| Risk | Impact | Mitigation |
|------|---------|-------------|
| AI hallucination | Medium | Implement validation checks and human-reviewed templates |
| Data privacy | High | Use encryption and minimal data retention |
| Low engagement | Medium | Add gamified progress and adaptive difficulty |

---

## 16. Ethical Considerations
- AI outputs reviewed for bias and accuracy.  
- User privacy and consent are prioritized.  
- Clear disclaimers that simulations are educational, not predictive.  

---

## 17. Future Enhancements
- Multi-language support.  
- AR/VR immersive career labs.  
- Integration with LinkedIn and career platforms.  
- Personalized skill-building suggestions.  

---

## 18. References
- O*NET Career Data  
- OpenAI Developer Documentation  
- React, FastAPI, AWS, and PostgreSQL official docs  

---

