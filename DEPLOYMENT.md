# Deploying to Vercel + Railway

This app is a **full-stack** application:
- `frontend/` — React (CRA) — deploys to **Vercel**
- `backend/` — FastAPI + MariaDB — deploys to **Railway** (Vercel cannot host long-running Python servers or MySQL)

---

## Step 1 — Deploy the backend to Railway

Vercel cannot run FastAPI as a long-running server, and cannot host MySQL. Use Railway for both.

1. Go to https://railway.app → **New Project** → **Deploy from GitHub repo**.
2. Select this repo. When asked for the **Root Directory**, set it to `backend`.
3. Railway will detect Python from `requirements.txt`. Add this **Start Command**:
   ```
   uvicorn server:app --host 0.0.0.0 --port $PORT
   ```
4. In the same Railway project, click **+ New** → **Database** → **Add MySQL**.
5. Once the MySQL service is running, Railway auto-injects `MYSQL_URL` (or you copy the connection URL from MySQL → Variables tab and add it to the backend service as `MYSQL_URL`).
   - Convert Railway's `mysql://...` URL to `mysql+pymysql://...` (just change the scheme) since the code uses PyMySQL.
6. In the backend service **Variables**, also add:
   - `CORS_ORIGINS=https://your-vercel-app.vercel.app` (your Vercel URL, comma-separated for multiple)
   - `CACHE_TTL_SECONDS=3600`
   - `GITHUB_API_BASE=https://api.github.com`
7. Deploy. Railway gives you a public URL like `https://your-backend.up.railway.app`.
8. Test: `curl https://your-backend.up.railway.app/api/` should return `{"service":"GitHub Profile Analyzer","status":"ok"}`.

---

## Step 2 — Deploy the frontend to Vercel

The repo now contains `vercel.json` at the root, which tells Vercel to build only the `frontend/` directory.

1. In your existing Vercel project → **Settings** → **Git** → re-deploy (or push a new commit to trigger build).
2. Go to **Settings** → **Environment Variables** and add:
   - `REACT_APP_BACKEND_URL` = the Railway URL from Step 1 (e.g., `https://your-backend.up.railway.app`)
3. Redeploy the Vercel project so the new env var is baked into the build.
4. Open the Vercel URL — the dashboard should load and successfully analyze GitHub users.

---

## How the pieces talk

```
[ Browser ]
     │
     ├──→ Vercel  →  serves React static build
     │
     └──→ Railway → FastAPI /api/* → MySQL (on Railway)
                       │
                       └──→ api.github.com (public, unauthenticated)
```

---

## Alternative: stay on a single platform

- **Everything on Railway**: deploy frontend as a second service (root `frontend`, build `yarn build`, output `build/`). Skip Vercel entirely.
- **Everything on Emergent**: requires migrating MySQL → MongoDB. Ask me and I can do that rewrite.
