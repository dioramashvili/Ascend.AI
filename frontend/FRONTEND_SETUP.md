# Frontend Setup Guide

## Connecting Frontend to Backend

The frontend is now configured to connect to your backend API. Follow these steps:

### 1. Environment Configuration

The frontend uses environment variables to configure the API URL. 

**For Production (connecting to Render backend):**

Create a `.env` file in the `frontend/` directory:

```bash
VITE_API_BASE_URL=https://ascend-ai-4pyg.onrender.com/api
```

**For Local Development:**

Create a `.env.local` file in the `frontend/` directory:

```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

> Note: `.env.local` files are automatically ignored by git (already in `.gitignore`)

### 2. Backend CORS Configuration

The backend needs to allow requests from your frontend origin. 

**If your frontend is deployed on a different domain** (e.g., Vercel, Netlify), you need to:

1. Set the `CORS_ORIGINS` environment variable in your Render backend:
   ```
   CORS_ORIGINS=https://your-frontend-domain.com,http://localhost:5173
   ```

2. Or update the backend code in `backend/app/config.py` to include your frontend URL in the default `cors_origins` list.

**For local development**, the backend already allows `http://localhost:5173` and `http://localhost:3000`.

### 3. Running the Frontend

```bash
cd frontend
npm install  # If you haven't already
npm run dev
```

The frontend will start on `http://localhost:5173` and connect to your backend.

### 4. Testing the Connection

1. Open the frontend in your browser
2. Enter a career title (e.g., "Product Manager")
3. Click "Generate Scenario"
4. The frontend should now connect to your Render backend at `https://ascend-ai-4pyg.onrender.com/api`

### Troubleshooting

**CORS Errors:**
- Make sure your frontend URL is included in the backend's `CORS_ORIGINS` environment variable
- Check that the backend is running and accessible
- Verify the API URL in your `.env` file matches your backend URL

**Connection Errors:**
- Verify the backend is running: `https://ascend-ai-4pyg.onrender.com/health`
- Check the browser console for detailed error messages
- Ensure the API URL in `.env` includes `/api` at the end

**Environment Variables Not Loading:**
- Make sure the `.env` file is in the `frontend/` directory (not `frontend/src/`)
- Restart the Vite dev server after creating/modifying `.env` files
- Vite only loads variables prefixed with `VITE_`

### Current Configuration

- **Backend URL:** `https://ascend-ai-4pyg.onrender.com`
- **API Base URL:** `https://ascend-ai-4pyg.onrender.com/api`
- **Frontend Dev Server:** `http://localhost:5173`

The frontend code in `src/App.tsx` now uses:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://ascend-ai-4pyg.onrender.com/api';
```

This means:
- If `VITE_API_BASE_URL` is set in `.env`, it will use that
- Otherwise, it defaults to the production backend URL

