# 🚀 How to Run the Project

**Project:** CareerSim – AI Career Experience Simulator  
**Team:** Ascend.AI

---

## Prerequisites

Before running the project, ensure you have:

- **Python 3.10+** installed
- **Node.js 18+** and **npm** installed
- **Git** installed
- **Gemini API Key** (from Google AI Studio)
- **Supabase** account and credentials (optional for local dev)

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/dioramashvili/Ascend.AI.git
cd Ascend.AI
```

---

## Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# Copy this template and fill in your values
# .env file should be in backend/.env
```

**Required Environment Variables:**

```env
# Application
APP_NAME=CareerSim
DEBUG=True
ENVIRONMENT=development
SECRET_KEY=your-secret-key-here-change-in-production

# Gemini AI (Required)
GEMINI_API_KEY=your-gemini-api-key-here

# Gemini Configuration (Optional - defaults provided)
GEMINI_MODEL_FLASH=gemini-2.5-flash
GEMINI_TEMPERATURE_GENERATION=0.7
GEMINI_TEMPERATURE_EVALUATION=0.3
GEMINI_MAX_TOKENS=2000

# Supabase (Optional for local dev - can use mock)
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# Redis (Optional - mock cache is used if not available)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Security
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100

# Logging
LOG_LEVEL=INFO

# CORS (Frontend URLs)
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

**Getting Your Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your `.env` file

### Step 5: Run the Backend Server

```bash
# From the backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start at: **http://localhost:8000**

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory

Open a new terminal window:

```bash
cd frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Run the Development Server

```bash
npm run dev
```

The frontend will start at: **http://localhost:5173**

---

## Running Both Services

### Option 1: Two Terminal Windows

**Terminal 1 (Backend):**
```bash
cd backend
# Activate venv if needed
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

### Option 2: Using a Process Manager

You can use tools like `concurrently` or `npm-run-all` to run both:

```bash
# Install concurrently globally
npm install -g concurrently

# Run both (from project root)
concurrently "cd backend && uvicorn app.main:app --reload" "cd frontend && npm run dev"
```

---

## Testing the Setup

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "app": "CareerSim",
  "environment": "development"
}
```

### 2. Test API Endpoint

```bash
curl -X POST http://localhost:8000/api/scenarios/generate \
  -H "Content-Type: application/json" \
  -d '{
    "career_title": "software engineer",
    "difficulty": "intermediate",
    "focus_area": "code review"
  }'
```

### 3. Open Frontend

Navigate to http://localhost:5173 in your browser.

---

## Running Lab 9 Performance Tests

To run the Lab 9 performance baseline tests:

```bash
# Make sure backend is running first
cd backend
python tests/performance/run_test_queries.py
```

This will:
- Run 40 test queries
- Measure latency, success rate, and token usage
- Generate `lab9_metrics.json` with results

---

## Troubleshooting

### Backend Issues

**Port Already in Use:**
```bash
# Windows: Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

**Module Not Found Errors:**
```bash
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

**Environment Variables Not Loading:**
- Ensure `.env` file is in the `backend` directory
- Check that variable names match exactly (case-sensitive)
- Restart the server after changing `.env`

### Frontend Issues

**Port Already in Use:**
- Vite will automatically try the next available port
- Or specify a different port: `npm run dev -- --port 3000`

**Dependencies Not Installing:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**CORS Errors:**
- Ensure backend CORS_ORIGINS includes your frontend URL
- Check that backend is running on port 8000
- Verify CORS middleware is configured correctly

### API Issues

**401 Unauthorized:**
- Check that your API keys are set correctly in `.env`
- Verify Gemini API key is valid

**500 Internal Server Error:**
- Check backend logs for detailed error messages
- Verify all required environment variables are set
- Ensure Supabase credentials are correct (if using)

---

## Development Workflow

### Making Changes

1. **Backend Changes:**
   - Edit files in `backend/app/`
   - Server auto-reloads with `--reload` flag
   - Check terminal for errors

2. **Frontend Changes:**
   - Edit files in `frontend/src/`
   - Browser auto-refreshes with Vite HMR
   - Check browser console for errors

### Code Quality

**Backend:**
```bash
# Run linter (if configured)
pylint app/

# Run type checking (if configured)
mypy app/
```

**Frontend:**
```bash
# Run linter
npm run lint

# Build for production
npm run build
```

---

## Production Deployment

### Backend

1. Set `DEBUG=False` and `ENVIRONMENT=production` in `.env`
2. Use a production ASGI server:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Frontend

1. Build the production bundle:
   ```bash
   npm run build
   ```
2. Serve the `dist` folder with a web server (nginx, Apache, etc.)

---

## Project Structure

```
Ascend.AI/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── models/          # Data models
│   │   └── main.py          # FastAPI app entry point
│   ├── tests/
│   │   └── performance/     # Lab 9 performance tests
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables (create this)
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main React component
│   │   └── main.tsx         # React entry point
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite configuration
│
└── docs/
    └── SETUP_INSTRUCTIONS.md # This file
```

---

## Additional Resources

- **API Documentation:** http://localhost:8000/docs (when backend is running)
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Docs:** https://react.dev/
- **Vite Docs:** https://vite.dev/

---

## Getting Help

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review backend logs in the terminal
3. Check browser console for frontend errors
4. Verify all environment variables are set correctly
5. Ensure all dependencies are installed

---

**Last Updated:** December 22, 2025

