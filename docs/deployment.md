# Deployment Guide

## What Can Be Hosted for Free?

There are two deployment modes:

1. Static demo on GitHub Pages.
2. Full-stack app with a hosted backend and frontend.

GitHub Pages can host static HTML, CSS, JavaScript, and images. It cannot run the FastAPI backend, so upload, server-side AI classification, persistent annotations, and database-backed search require a backend host.

## GitHub Pages Static Demo

This repository includes `.github/workflows/pages.yml`. When pushed to GitHub, it:

1. Generates a static demo library from the included Pexels evaluation dataset.
2. Builds the React frontend with `VITE_STATIC_DEMO=true`.
3. Publishes `frontend/dist` to GitHub Pages.

The static demo lets users browse, search, filter, inspect AI metadata, and add annotations in the current browser session. It does not upload new images or call OpenAI.

After pushing to GitHub:

1. Open the repository on GitHub.
2. Go to `Settings` > `Pages`.
3. Set the source to `GitHub Actions`.
4. Run or wait for the `Deploy static demo to GitHub Pages` workflow.
5. The published URL will look like:

```text
https://srilatham819.github.io/fashion-garment-classification-inspiration-web-app/
```

## Full-Stack Free Preview

For real upload/classify/search behavior online, deploy the backend to a service that supports Python web services and deploy the frontend as a static site.

One workable free-preview setup:

- Backend: Render free web service.
- Database: Render free PostgreSQL, or SQLite only for short-lived previews.
- Frontend: GitHub Pages, Render static site, Netlify, or Vercel.

Backend build command:

```bash
cd backend && pip install -e .
```

Backend start command:

```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set backend environment variables on the host:

```text
DATABASE_URL=your_database_url
OPENAI_API_KEY=your_openai_key
UPLOAD_STORAGE_PATH=/tmp/uploads
FAISS_INDEX_PATH=/tmp/fashion.index
DEMO_AI_FALLBACK=true
```

Set frontend environment variable before building:

```text
VITE_API_BASE_URL=https://your-backend-host.example.com/api
```

## Important Hosting Caveats

- Free web services can sleep when idle, so the first request may be slow.
- Local filesystem uploads may disappear on hosts with ephemeral disks. Use S3, R2, GCS, or another persistent object store for production.
- SQLite is fine for local demos, but PostgreSQL is a better hosted target.
- Do not expose secret keys in frontend environment variables. `OPENAI_API_KEY` and `PEXELS_API_KEY` belong only on the backend or in local scripts.

