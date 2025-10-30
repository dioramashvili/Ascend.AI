

## 1. Architecture Evolution

The architecture has progressively matured to meet growing demands for better state management, security, scalability, and cost optimization.

| Component | Initial (Week 2) | Mid-Point (Week 4) | Current Recommended | Reason for Change |
|------------|--------|--------|------------------|--------|
| Frontend | Basic React | React + Vite | React + Zustand + React Query + Error Boundary | Superior state management, data fetching, and UX. |
| Backend | Flask | FastAPI | FastAPI + JWT + Rate Limiting + Celery + Pydantic | Security, scalability, async efficiency, and data integrity. |
| Database | Supabase | PostgreSQL | PostgreSQL + SQLAlchemy ORM + Alembic Migrations | Reliability, performance, and maintainable schema evolution. |
| AI Model | GPT | Gemini Pro + Flash | Gemini Pro + Flash | Best latency-cost balance for core functionality. |
| Cache Layer | None | None | Redis | Drastically reduces API costs and improves latency. |
| Deployment | Manual | Manual | Docker Containers + CI/CD | Consistency, portability, and automated deployments. |

---

## 2. Current Architecture Diagram

```
┌─────────────┐      ┌────────────────────────┐       ┌────────────────────────┐
│   User      │─────▶│  Frontend (React)      │─────▶│   Backend (FastAPI)    │
│  (Browser)  │      │  + Zustand/ReactQuery  │◀─────│  + JWT + Celery + Pydantic │
└─────────────┘      └────────────────────────┘       └─────────────┬──────────┘
                                                                    │
                           ┌────────────────────────────────────────┼───────────────────┐
                           │                                        │                   │
                           ▼                                        ▼                   ▼
                    ┌──────────────┐                       ┌──────────────┐    ┌─────────────┐
                    │ Redis Cache  │                       │ Gemini API   │    │ PostgreSQL  │
                    │ (Responses & │                       │ (Evaluation) │    │ (SQLAlchemy │
                    │   Task Queue)│                       │ + Fallback   │    │ + Alembic)  │
                    └──────────────┘                       └──────────────┘    └─────────────┘
```

---

## 3. Component Deep Dive & Recommendations

### 3.1. Frontend (React)

#### (High Priority) Adopt Zustand for State Management
Zustand offers a minimalistic yet powerful global state management solution.

```tsx
// store/useGameStore.ts
import { create } from 'zustand';

interface GameState {
  balance: number;
  setBalance: (value: number) => void;
}

export const useGameStore = create<GameState>((set) => ({
  balance: 100,
  setBalance: (value) => set({ balance: value }),
}));
```

#### (High Priority) Use React Query for Data Fetching
React Query simplifies API calls, caching, and state synchronization with the server.

```tsx
import { useQuery } from '@tanstack/react-query';

function useScenarios() {
  return useQuery({
    queryKey: ['scenarios'],
    queryFn: async () => (await fetch('/api/scenarios')).json(),
  });
}
```

#### (Medium Priority) Add Global Error Boundary
A global error boundary improves user experience by gracefully handling runtime failures.

```tsx
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) return <h1>Something went wrong.</h1>;
    return this.props.children;
  }
}
```

### 3.2. Backend (FastAPI)

#### (Critical) Implement Strict Input Validation with Pydantic
This is the first line of defense against malformed or malicious data. By strictly defining the shape of expected data, you prevent a huge class of vulnerabilities.

**1. Define Pydantic Models (`schemas.py`):**
```python
# schemas.py
from pydantic import BaseModel, Field, constr

class ScenarioRequest(BaseModel):
    career_title: constr(strip_whitespace=True, to_lower=True, min_length=3, max_length=100)

class ScenarioResponse(BaseModel):
    scenario: str
    options: list[str]

class EvaluationRequest(BaseModel):
    career_title: constr(strip_whitespace=True, to_lower=True, min_length=3, max_length=100)
    user_answer: constr(strip_whitespace=True, min_length=1, max_length=500)

class EvaluationResponse(BaseModel):
    feedback: str
    score: int = Field(..., ge=0, le=10) # Ensures score is between 0 and 10
```

**2. Use Models in Endpoints (`main.py`):**
```python
# main.py
import schemas
from fastapi import FastAPI

app = FastAPI()

@app.post("/generate-scenario", response_model=schemas.ScenarioResponse)
async def generate_scenario(request: schemas.ScenarioRequest):
    # `request.career_title` is now guaranteed to be clean and valid.
    # FastAPI automatically handles validation and returns a 422 error on failure.
    # ... logic to call Gemini ...
    return {"scenario": "A new challenge awaits...", "options": ["A", "B", "C"]}
```

#### (Critical) Implement Robust Authentication (JWT)
Secures your API and manages user access using standard, stateless authentication.

**1. Create `auth.py`:**
```python
# auth.py
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY", "a_very_insecure_default_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # ... (implementation from original file)
```

**2. Integrate into `main.py`:**
Add `/token` and protected user endpoints as shown in the original file.

#### (Critical) Add API Rate Limiting
Prevents abuse, protects your application from DoS attacks, and controls Gemini API costs.

```python
# main.py
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/generate-scenario")
@limiter.limit("10/minute") # Example: Limit to 10 requests per minute per IP
async def generate_scenario(request: Request, data: dict):
    # ... endpoint logic
    return {"scenario": "A new challenge awaits..."}
```

#### (High Priority) Introduce a Background Task Queue (Celery)
Handles long-running Gemini evaluations asynchronously, preventing request timeouts and improving user experience.

**1. Create `celery_worker.py`:**
```python
# celery_worker.py
from celery import Celery

celery_app = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

@celery_app.task
def evaluate_user_choice_task(career_title: str, user_answer: str):
    # Simulate a long-running AI call
    import time
    time.sleep(5)
    return {"feedback": f"Your choice '{user_answer}' was insightful.", "score": 8}
```

**2. Add Endpoints in `main.py`:**
Create endpoints to dispatch tasks (`/evaluate-answer`) and poll for results (`/tasks/{task_id}`).

#### (High Priority) Implement a Caching Layer (Redis)
Drastically reduces costs and latency for repeated requests (e.g., generating a scenario for the same career title).

**1. Create a Caching Decorator (`caching.py`):**
```python
# caching.py
import functools
import json
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
CACHE_TTL = 60 * 60 * 24 # 24 hours

def cache_response(ttl: int = CACHE_TTL):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate a unique key based on function name and args
            key_parts = [func.__name__] + [str(a) for a in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
            cache_key = ":".join(key_parts)

            # 1. Try to get from cache
            if cached_result := redis_client.get(cache_key):
                return json.loads(cached_result)

            # 2. If miss, call original function
            result = await func(*args, **kwargs)

            # 3. Store result in cache
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

**2. Apply Decorator to Service Function:**
```python
# gemini_service.py
from caching import cache_response

@cache_response(ttl=3600) # Cache for 1 hour
async def generate_scenario_from_gemini(career_title: str, prompt_version: str):
    # ... logic to call Gemini API ...
```

#### (Medium Priority) Develop a Graceful Fallback & Retry System
Improves application reliability when external APIs like Gemini fail or are slow.

**1. Install `tenacity` for Retries:**
```bash
pip install tenacity
```

**2. Combine Retry and Fallback in Your Service:**
```python
# gemini_service.py
import json
from tenacity import retry, stop_after_attempt, wait_fixed
from fastapi import HTTPException

class GeminiAPIError(Exception): pass

# Load fallback scenarios from a JSON file or database
with open("fallback_scenarios.json", "r") as f:
    FALLBACK_SCENARIOS = json.load(f)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def generate_with_retry(prompt: str):
    # ... wrapper for the actual Gemini API call ...

async def get_scenario_with_fallback(career_title: str):
    try:
        return await generate_with_retry(f"Generate scenario for {career_title}...")
    except Exception:
        if fallback := FALLBACK_SCENARIOS.get(career_title):
            return fallback
        raise HTTPException(status_code=503, detail="AI service is temporarily unavailable.")
```

#### (Medium Priority) Externalize Prompt Management
Moves prompts from hardcoded strings to a database table, allowing for easy testing, versioning, and iteration without redeploying the application.

**1. Define `prompt_templates` Table in PostgreSQL:**
```sql
CREATE TABLE prompt_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    version INT NOT NULL,
    template_text TEXT NOT NULL,
    is_active BOOLEAN DEFAULT FALSE
);
```

**2. Use Dynamic Prompts in Your Logic:**
Your service should first query this table for the active prompt template, format it with runtime variables (like `career_title`), and then send it to the Gemini API.

### 3.3. Data Layer (PostgreSQL)

#### (Critical) Plan and Document Your Schema with an ORM
A well-designed schema ensures data integrity and performance. Using an ORM like SQLAlchemy keeps your schema definition version-controlled with your application code.

**1. Define Models (`models.py`):**
```python
# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    sessions = relationship("SimulationSession", back_populates="user")

class SimulationSession(Base):
    __tablename__ = "simulation_sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    career_title = Column(String(100), nullable=False)
    user = relationship("User", back_populates="sessions")

# ... other models like UserResponse
```

**2. Use Alembic for Database Migrations:**
Alembic manages incremental changes to your schema, ensuring your database state always matches your models.
```bash
# 1. Initialize Alembic
alembic init alembic

# 2. Configure alembic.ini and alembic/env.py to point to your DB and models

# 3. Create a migration script automatically
alembic revision --autogenerate -m "Create initial tables"

# 4. Apply the migration to the database
alembic upgrade head
```

#### (High Priority) Use a Connection Pooler
Reusing database connections dramatically improves performance. SQLAlchemy has a powerful built-in pooler that is configured when creating the engine.

**1. Create a Central Database Module (`database.py`):**
```python
# database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, pool_size=10, max_overflow=20)
AsyncSessionFactory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Dependency for FastAPI endpoints
async def get_db_session():
    async with AsyncSessionFactory() as session:
        yield session
```

#### (Critical) Implement Automated Backups
This is a non-negotiable step to prevent catastrophic data loss.

*   **Recommended:** Use your cloud provider's (AWS RDS, Google Cloud SQL) built-in automated backup and point-in-time recovery features. This is the most reliable method.
*   **Self-Hosted:** Use a cron job to run `pg_dump` daily and store the compressed backup file in a secure location (like an S3 bucket).

### 3.4. DevOps & Operations

#### (High Priority) Containerize the Application (Docker)
Docker ensures your application runs identically across all environments (local, staging, production), eliminating "it works on my machine" issues.

**1. Create `Dockerfile.backend` for FastAPI:**
```dockerfile
# Dockerfile.backend
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**2. Create `Dockerfile` for React Frontend (Multi-stage):**
```dockerfile
# frontend/Dockerfile
# --- Build Stage ---
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# --- Serve Stage ---
FROM nginx:stable-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf # Custom config to proxy /api to backend
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**3. Orchestrate with `docker-compose.yml`:**
A docker-compose file brings up the entire stack (frontend, backend, database, redis) with a single command for easy local development.

#### (Critical) Implement Structured Logging & Error Tracking
When your app is running on a server, `print()` is useless. Structured (JSON) logs are machine-readable for analysis, and error tracking alerts you to crashes instantly.

**1. Configure Structured Logging with `structlog`:**
```python
# main.py
import structlog
# ... (configuration from original file) ...
log = structlog.get_logger()

@app.get("/")
async def root():
    log.info("root.endpoint.called", user_ip="127.0.0.1")
    return {"message": "Hello World"}
```

**2. Integrate an Error Tracker like Sentry:**
```bash
pip install sentry-sdk[fastapi]
```
```python
# main.py
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN_HERE",
    traces_sample_rate=1.0,
)
```

#### (High Priority) Set Up a CI/CD Pipeline (GitHub Actions)
Automate testing and publishing of your Docker images to remove manual, error-prone deployment steps.

**Create `.github/workflows/ci-cd.yml`:**
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline
on:
  push:
    branches: [ "main" ]

jobs:
  test-and-build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies and run tests
      run: |
        pip install -r requirements.txt
        # pytest
    - name: Log in to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    - name: Build and push backend image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./Dockerfile.backend
        push: true
        tags: your-username/careersim-backend:latest
```

### 3.5. Security

#### (High Priority) Use a Dedicated Secret Manager
Never hardcode secrets or commit them to git. A secret manager provides a secure, centralized way to manage API keys and database credentials.

**1. Use `.env` file for local development:**
Use `python-dotenv` and Pydantic's `BaseSettings` to load secrets from a `.env` file (which is added to `.gitignore`).

**2. Use a Cloud Secret Manager in Production (e.g., AWS Secrets Manager):**
Your application code should be written to fetch secrets from the cloud provider's service at runtime when in a production environment.

#### (Medium Priority) Automate Dependency Scanning
Your application's dependencies can contain vulnerabilities. Automated tools are essential for detection and patching.

**Enable GitHub Dependabot:**
1.  Go to your repository's **Settings > Code security and analysis**.
2.  Enable **Dependabot alerts** and **Dependabot security updates**.
3.  (Optional) Add a `.github/dependabot.yml` file to configure automatic pull requests for keeping dependencies up-to-date, not just patched for vulnerabilities.

---

## 4. Implementation Priority Plan

This phased plan prioritizes tasks to build a strong foundation first, then adds performance and resilience features.

#### Phase 1: Core Foundation (Critical Priority)
*   **Data:** Plan schema with SQLAlchemy models & create the first Alembic migration.
*   **Backend:** Implement strict input validation with Pydantic for all endpoints.
*   **Security:** Implement JWT Authentication for user management.
*   **Backend:** Add API Rate Limiting to all critical endpoints.
*   **DevOps:** Containerize all services (Backend, Frontend, DB, Redis) with Docker and Docker Compose.
*   **Security:** Set up secret management using `.env` for local and a plan for production.
*   **Data:** Verify automated database backups are enabled.

#### Phase 2: Performance & Reliability (High Priority)
*   **Backend:** Implement Redis Caching for expensive AI API calls.
*   **Backend:** Implement Celery for asynchronous task processing.
*   **DevOps:** Set up structured logging (structlog) and error tracking (Sentry).
*   **Data:** Ensure the database connection pool is properly configured in the application.
*   **Frontend:** Implement React Query for efficient data fetching and caching.

#### Phase 3: Automation & Resilience (High Priority)
*   **DevOps:** Create a basic CI/CD pipeline in GitHub Actions to test and publish Docker images.
*   **Security:** Enable Dependabot for automated dependency scanning and alerts.
*   **Backend:** Implement a retry mechanism (`tenacity`) and a graceful fallback system for the Gemini API.
*   **Frontend:** Implement Zustand for global state management.

#### Phase 4: Optimization & Maintainability (Medium Priority)
*   **Backend:** Externalize prompt management into a PostgreSQL table.
*   **Frontend:** Add a global Error Boundary to the React application.
*   **DevOps:** Expand the CI/CD pipeline to include automated deployment steps.
