# 4. Technical Architecture (Updated – Week 6)

## Architecture Evolution

| Component | Week 2 | Week 4 | Week 6 (Current) | Reason |
|------------|---------|---------|------------------|--------|
| **Frontend** | Basic React | React + Vite (optimized) | React + Vite + Zustand + React Query + Error Boundary | Faster UI, predictable global state, cached API data, resilient error handling |
| **Backend** | Flask | FastAPI | FastAPI (no change) | Needed async for Gemini |
| **Database** | Supabase | PostgreSQL | PostgreSQL (no change) | Chosen for reliability |
| **AI Model** | OpenAI GPT | Gemini Pro + Flash | Gemini Pro + Flash | Better latency-cost balance |

---

## Current Architecture Diagram

```
                ┌──────────────────────────────┐
                │          User                │
                │        (Browser)             │
                └──────────────┬───────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │         Frontend             │
                │  React + Vite                │
                │  ├─ Zustand (Global Store)   │
                │  ├─ React Query (Data Layer) │
                │  └─ Error Boundary (Resilience)
                └──────────────┬───────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │          Backend             │
                │          FastAPI             │
                └──────────────┬───────────────┘
                               │
           ┌────────────┬──────────────┬────────────┐
           ▼            ▼              ▼            ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐
    │ Gemini   │  │ Map API  │  │PostgreSQL│  │ Auth Layer │
    │   API    │  │(Routes)  │  │   DB     │  │ (Supabase) │
    └──────────┘  └──────────┘  └──────────┘  └────────────┘
```

**Note:**  
- **Zustand** manages simulation-related global state across components.  
- **React Query** handles data fetching, caching, and synchronization with FastAPI.  
- **Error Boundary** ensures the app remains stable even when a component fails.  
- **Map API** still represents visualized learning paths for user progress.  

---

## Frontend Architecture Details

### (High Priority) Adopt a State Management Library (Zustand)

**Purpose:** Manage global state for simulation flow (career choice, current scenario, user score, etc.) without prop drilling.

#### Setup

```bash
npm install zustand
```

#### Store Example

```javascript
// src/store/simulationStore.js
import { create } from 'zustand';

export const useSimulationStore = create((set) => ({
  careerTitle: null,
  currentScenario: null,
  userScore: 0,
  isLoading: false,
  error: null,

  startSimulation: (title) =>
    set({
      careerTitle: title,
      userScore: 0,
      currentScenario: null,
      isLoading: true,
      error: null,
    }),

  setScenario: (scenarioData) =>
    set({ currentScenario: scenarioData, isLoading: false }),

  updateScore: (points) =>
    set((state) => ({ userScore: state.userScore + points })),

  setError: (errorMessage) =>
    set({ isLoading: false, error: errorMessage }),

  resetSimulation: () =>
    set({
      careerTitle: null,
      currentScenario: null,
      userScore: 0,
      isLoading: false,
      error: null,
    }),
}));
```

#### Usage Example

```jsx
// src/components/CareerSelector.jsx
import React from 'react';
import { useSimulationStore } from '../store/simulationStore';

function CareerSelector() {
  const startSimulation = useSimulationStore((state) => state.startSimulation);

  return (
    <div>
      <h2>Choose a Career Path</h2>
      <button onClick={() => startSimulation('Software Engineer')}>
        Start as Software Engineer
      </button>
    </div>
  );
}
```

---

### (High Priority) Use a Data Fetching Library (React Query)

**Purpose:** Simplify fetching and caching from FastAPI, reduce boilerplate, and handle retries automatically.

#### Setup

```bash
npm install @tanstack/react-query
```

#### Provider Configuration

```jsx
// src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);
```

#### Fetch Example

```javascript
// src/api/careerSimApi.js
import axios from 'axios';

export const fetchScenario = async (careerTitle) => {
  const { data } = await axios.post('/api/generate-scenario', {
    career_title: careerTitle,
  });
  return data;
};
```

#### Using React Query in a Component

```jsx
// src/components/ScenarioDisplayWithData.jsx
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchScenario } from '../api/careerSimApi';
import { useSimulationStore } from '../store/simulationStore';

function ScenarioDisplayWithData() {
  const careerTitle = useSimulationStore((state) => state.careerTitle);

  const { data, error, isLoading } = useQuery({
    queryKey: ['scenario', careerTitle],
    queryFn: () => fetchScenario(careerTitle),
    enabled: !!careerTitle,
  });

  if (isLoading) return <div>Generating your scenario...</div>;
  if (error) return <div>An error occurred: {error.message}</div>;

  return (
    <div>
      {data ? (
        <>
          <h3>Scenario for: {careerTitle}</h3>
          <p>{data.scenario}</p>
          <ul>
            {data.options.map((option, i) => (
              <li key={i}>
                <button>{option}</button>
              </li>
            ))}
          </ul>
        </>
      ) : (
        <div>Please select a career to begin.</div>
      )}
    </div>
  );
}
```

---

### (Medium Priority) Implement a Global Error Boundary

**Purpose:** Prevent the entire app from crashing on unexpected component errors.

#### Component

```jsx
// src/components/ErrorBoundary.jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error('Uncaught error:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div>
          <h2>Something went wrong.</h2>
          <p>Please refresh the page or try again later.</p>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
```

#### Usage

```jsx
// src/App.jsx
import React from 'react';
import ErrorBoundary from './components/ErrorBoundary';
import CareerSelector from './components/CareerSelector';
import ScenarioDisplayWithData from './components/ScenarioDisplayWithData';

function App() {
  return (
    <ErrorBoundary>
      <header><h1>CareerSim</h1></header>
      <main>
        <CareerSelector />
        <ScenarioDisplayWithData />
      </main>
    </ErrorBoundary>
  );
}

export default App;
```

---

### Summary of Frontend Benefits

| Feature | Library | Key Advantage |
|----------|----------|----------------|
| Global State | Zustand | Minimal boilerplate, simple API |
| Data Fetching | React Query | Automatic caching & retry |
| Error Handling | Error Boundary | Prevents total app crash |
| UI Performance | Vite + React | Fast reload, modular setup |

---

**Next Steps (Future Considerations)**  
- Integrate **lazy loading** for large components.  
- Add **Sentry or LogRocket** for centralized error logging.  
- Implement **dark mode & responsive design** for better UX.
