# Fashion Garment Classification & Inspiration Web App

Complete technical documentation for Srilatha.

## 1. Project Summary

This project is a lightweight full-stack AI web application for fashion designers who collect inspiration photos from stores, markets, travel, streetwear, and trend research. The app lets designers upload garment photos, automatically classify them with AI, browse the resulting image library, search/filter by fashion metadata, and add designer annotations over time.

The project is intentionally scoped as a proof of concept. It demonstrates the end-to-end workflow, clean architecture, AI integration boundaries, evaluation thinking, and test coverage without trying to become a production asset management system.

## 2. Case Study Requirements

The source document asks for a lightweight AI-powered web app that helps fashion designers organize, search, and reuse inspiration imagery captured in the field. The required capabilities are:

- A web app for uploading garment photos.
- AI classification using a multimodal model.
- Natural-language description plus structured fashion attributes.
- Storage for AI metadata.
- Visual image library grid.
- Dynamic filters across garment metadata.
- Contextual filters for location, time, season, and designer.
- Full-text search across image descriptions.
- Designer annotations with tags and notes.
- Searchable annotations clearly separated from AI metadata.
- A 50-100 image evaluation set from an open-source source such as Pexels.
- Expected labels, classifier run, per-field accuracy, and written evaluation summary.
- Unit, integration, and end-to-end tests.
- Clear README and architectural explanation.
- Honest tradeoffs and limitations.

## 3. Requirement Verification

| Requirement | Status | Implementation |
| --- | --- | --- |
| Upload photos | Complete | FastAPI upload endpoint stores files locally and creates image rows. |
| AI classification | Complete | OpenAI vision adapter when an API key is configured; deterministic fallback for local/demo use. |
| Structured metadata | Complete | Garment type, style, material, color palette, pattern, season, occasion, consumer profile, trend notes, location context, and description. |
| Metadata persistence | Complete | SQLAlchemy models persist images, AI metadata, annotations, and vector references. |
| Visual grid | Complete | React image library grid. |
| Dynamic filters | Complete | Frontend generates facets from loaded library metadata. |
| Attribute filters | Complete | Garment type, style, material, color, pattern, season, occasion, consumer profile, and location context. |
| Context filters | Complete | Location text, continent/country/city style matching, year, month, season, and designer. |
| Full-text search | Complete | Search checks AI descriptions, trend notes, structured fields, location, and annotation text. |
| Designer annotations | Complete | Notes, tags, author, and timestamps stored separately from AI metadata. |
| Evaluation set | Complete | 80 Pexels images are included under `eval/dataset/images`. |
| Evaluation reports | Complete | `eval/reports/eval_summary.md` and generated JSON reports. |
| Tests | Complete | Unit, integration, and end-to-end backend tests. |
| Documentation | Complete | README plus this technical documentation. |

Nothing from the case-study document is intentionally omitted. The only important caveat is evaluation label quality: the included 80-image Pexels dataset satisfies the requested size, but its labels are starter labels derived from query buckets and marked for manual review. A stronger production evaluation would manually verify every image label.

## 4. Technology Stack

### Frontend

- React
- TypeScript
- Vite
- CSS
- Fetch API

How it is used:

- React builds the single-page interface.
- TypeScript gives typed API responses, request payloads, image metadata, and annotations.
- Vite provides fast local development and production builds.
- CSS handles responsive layout, image cards, filters, status badges, detail panel, and form styling.
- Fetch API calls the FastAPI backend for health checks, images, upload, search, and annotations.

Important files:

- `frontend/src/App.tsx`: main UI and workflows.
- `frontend/src/api/client.ts`: API client and TypeScript types.
- `frontend/src/styles/global.css`: application styling.
- `frontend/vite.config.ts`: Vite setup.

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL target database
- SQLite-compatible local/test mode
- FAISS
- OpenAI SDK
- Pillow

How it is used:

- FastAPI exposes REST endpoints.
- Pydantic validates request and response schemas.
- SQLAlchemy models and repositories persist images, AI metadata, annotations, and vector references.
- PostgreSQL is the intended durable database.
- SQLite support keeps tests and local demos simple.
- FAISS stores local semantic vectors for search.
- OpenAI SDK connects to multimodal image classification and text embeddings.
- Pillow supports local fallback image analysis.

Important files:

- `backend/app/main.py`: app factory and middleware.
- `backend/app/api/routes/images.py`: upload/list/detail/file endpoints.
- `backend/app/api/routes/search.py`: hybrid search endpoint.
- `backend/app/api/routes/annotations.py`: designer annotation endpoint.
- `backend/app/services/classification.py`: classification workflow.
- `backend/app/services/openai_vision.py`: OpenAI vision adapter and fallback classifier.
- `backend/app/services/search.py`: hybrid search logic.
- `backend/app/services/semantic_index.py`: description embedding and vector search.
- `backend/app/repositories/metadata.py`: SQL filtering and text matching.
- `backend/app/vector/faiss_index.py`: FAISS adapter with NumPy fallback behavior.

### Evaluation

- Python scripts
- Pexels dataset
- JSON labels
- Markdown summary report

How it is used:

- `eval/scripts/prepare_pexels_dataset.py` downloads 50-100 fashion photos from Pexels when `PEXELS_API_KEY` is set.
- `eval/dataset/images` contains the downloaded image set.
- `eval/dataset/labels/labels.json` stores expected labels.
- `eval/scripts/run_eval.py` runs classification and compares predictions to expected fields.
- `eval/reports/eval_summary.md` explains accuracy, confusion, strengths, and weaknesses.

### Testing

- Pytest
- FastAPI TestClient
- Deterministic hash embeddings
- Temporary SQLite database

How it is used:

- Unit tests validate parsing AI model output into structured attributes.
- Integration tests validate search filters, including location/time/designer/annotation behavior.
- E2E backend test validates upload, classification, and search filtering in one flow.
- Deterministic hash embeddings keep semantic tests fast and independent of OpenAI network calls.

Important tests:

- `backend/tests/unit/test_json_parsing.py`
- `backend/tests/integration/test_search_filters.py`
- `backend/tests/integration/test_semantic_retrieval.py`
- `backend/tests/integration/test_upload_flow.py`
- `backend/tests/e2e/test_upload_classify_filter.py`

## 5. Architecture

The app follows a layered structure:

```text
React frontend
  |
  | REST requests
  v
FastAPI routes
  |
  v
Application services
  |
  +-- upload orchestration
  +-- AI classification
  +-- semantic indexing
  +-- hybrid search
  |
  v
Repositories / adapters
  |
  +-- SQLAlchemy database access
  +-- local file storage
  +-- OpenAI API adapter
  +-- FAISS vector index
```

Why this structure:

- Routes stay thin and focus on HTTP concerns.
- Services hold business workflows.
- Repositories isolate database logic.
- Adapters isolate external systems such as OpenAI, local storage, and FAISS.
- Tests can swap out expensive or network-dependent pieces.

## 6. Data Model

### `images`

Stores:

- original filename
- storage path
- MIME type
- processing status
- error message
- created and updated timestamps

### `ai_metadata`

Stores:

- garment type
- style
- material
- color palette
- pattern
- season
- occasion
- consumer profile
- trend notes
- location context
- natural-language description
- raw model response
- model name

### `user_annotations`

Stores:

- image id
- designer note
- designer tags
- author/designer name
- timestamps

### `embedding_references`

Stores:

- image id
- FAISS vector id
- embedding model
- source field used for embedding

## 7. Main User Workflow

1. Designer opens the website.
2. Designer uploads a garment photo.
3. Backend validates file type and size.
4. File is saved to local storage.
5. Image row is created as `pending`.
6. Classification runs in the background.
7. AI metadata and description are generated.
8. Metadata is saved to the database.
9. Description is embedded.
10. Embedding is written to FAISS.
11. Image status changes to `classified`.
12. Designer searches, filters, opens details, and adds annotations.

## 8. Search and Filtering

The search approach is hybrid:

- Structured SQL filters handle deterministic fields.
- Text matching handles natural-language query terms, trend notes, location context, and annotations.
- Semantic search uses embeddings over AI descriptions.

Supported filters:

- garment type
- style
- material
- color
- pattern
- season
- occasion
- consumer profile
- location context
- continent/country/city style location matching
- year
- month
- designer
- annotation text/tags

Dynamic filters:

- The frontend builds filter options from the image library it receives from the backend.
- This avoids hardcoding filter values and lets new AI metadata automatically become filterable.

## 9. AI Classification

The classifier is designed around a strict JSON schema.

Expected output fields:

- `garment_type`
- `style`
- `material`
- `color_palette`
- `pattern`
- `season`
- `occasion`
- `consumer_profile`
- `trend_notes`
- `location_context`
- `description`

Important prompt principle:

- The model is instructed to return `unknown` when a field cannot be visually inferred.
- This matters because fashion metadata can easily become speculative, especially material, occasion, location, and consumer profile.

OpenAI mode:

- Set `OPENAI_API_KEY`.
- The adapter sends image content to a multimodal model.
- The response is parsed and validated.

Fallback mode:

- Used when no OpenAI key is configured.
- Uses filename and pixel/color cues to create deterministic metadata.
- Good for demos and tests.
- Not intended as a high-quality visual classifier.

## 10. Evaluation Approach

The evaluation pipeline:

1. Loads labels from `eval/dataset/labels/labels.json`.
2. Runs the classifier for each image.
3. Compares predictions to expected values.
4. Calculates per-field accuracy.
5. Records confusion analysis.
6. Writes JSON and Markdown reports.

The dataset:

- 80 Pexels fashion images.
- Images are grouped by searches such as black dress, red dress, streetwear jacket, white shirt, and floral skirt.
- Attribution is stored in `eval/dataset/pexels_attribution.json`.

Important evaluation caveat:

- The labels are starter labels derived from query buckets and marked for manual review.
- A stronger evaluation would manually inspect and correct every label.
- This limitation is documented honestly in the evaluation notes.

Why this still helps:

- It proves the pipeline is reproducible.
- It provides per-field metrics.
- It reveals where model behavior is weak.
- It creates a framework for future prompt/model comparisons.

## 11. Local Setup Instructions

The project has two running parts:

- Backend API: FastAPI service that stores images, classifies them, saves metadata, searches, and stores annotations.
- Frontend website: React/Vite app that calls the backend API.

Run the backend and frontend in two separate terminal windows.

### 11.1 Prerequisites

Install these before starting:

- Python 3.11 or newer. Python 3.12 is recommended.
- Node.js 20 or newer.
- npm, which is normally installed with Node.js.
- Optional: Docker Desktop if you want PostgreSQL through `docker-compose`.
- Optional: OpenAI API key if you want real multimodal classification instead of the local fallback.
- Optional: Pexels API key if you want to download a fresh evaluation image set.

### 11.2 Backend Setup, Command by Command

Start from the repository root:

```bash
cd /path/to/fashion-garment-classification-inspiration-web-app
```

Purpose:

- Moves your terminal into the root folder of the project.
- All relative paths in later commands assume this location.

Move into the backend folder:

```bash
cd backend
```

Purpose:

- The backend Python package and `pyproject.toml` live in this folder.
- Running install/test commands here lets Python find the backend configuration.

Create a Python virtual environment:

```bash
python3.12 -m venv .venv
```

Purpose:

- Creates an isolated Python environment in `backend/.venv`.
- Keeps project dependencies separate from your system Python.
- If your machine uses `python3` instead of `python3.12`, use `python3 -m venv .venv`.

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Purpose:

- Makes `python` and `pip` point to the project-specific environment.
- You should see `(.venv)` in your terminal prompt after this command.

Install backend dependencies:

```bash
python -m pip install -e ".[test]"
```

Purpose:

- Installs the backend package in editable mode.
- Installs runtime dependencies such as FastAPI, SQLAlchemy, OpenAI SDK, FAISS, Pillow, and Uvicorn.
- Installs test dependencies such as Pytest and HTTPX.
- Editable mode means code changes are picked up without reinstalling.

### 11.3 Backend Environment Variables

Environment variables configure where the backend stores data and whether it uses real AI services.

Use SQLite for a simple local demo:

```bash
export DATABASE_URL=sqlite:///./demo.db
```

Purpose:

- Tells SQLAlchemy to use a local SQLite database file named `backend/demo.db`.
- This is easiest for demos because you do not need PostgreSQL running.
- The production-style default is PostgreSQL, but SQLite is supported for local setup and tests.

Set the upload storage folder:

```bash
export UPLOAD_STORAGE_PATH=storage/uploads
```

Purpose:

- Tells the backend where to save uploaded image files.
- Because this command is run from `backend`, files are saved under `backend/storage/uploads`.
- This folder is ignored by Git so uploaded local files are not committed.

Set the vector index path:

```bash
export FAISS_INDEX_PATH=../infra/faiss/demo.index
```

Purpose:

- Tells the semantic search layer where to store the FAISS vector index.
- FAISS stores embeddings for AI-generated descriptions.
- The path points to `infra/faiss/demo.index` from the backend folder.

Enable local fallback classification:

```bash
export DEMO_AI_FALLBACK=true
```

Purpose:

- Lets the app classify images even when no OpenAI key is configured.
- The fallback uses simple filename and pixel/color cues.
- This is useful for local demos and tests, but it is not the high-quality AI path.

Optional: enable real OpenAI multimodal classification:

```bash
export OPENAI_API_KEY=your_openai_key
```

Purpose:

- Allows the backend to call OpenAI for image classification and text embeddings.
- Without this, the local fallback classifier is used.
- Do not put this key in frontend code or commit it to Git.

Optional: choose model names:

```bash
export OPENAI_VISION_MODEL=gpt-5.4-mini
export OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

Purpose:

- `OPENAI_VISION_MODEL` controls which multimodal model classifies images.
- `OPENAI_EMBEDDING_MODEL` controls which embedding model indexes descriptions for semantic search.
- Defaults already exist, so these exports are only needed if you want to override them.

### 11.4 Start the Backend

Run this from the `backend` folder with the virtual environment activated:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Purpose:

- Starts the FastAPI API server.
- `app.main:app` points Uvicorn to the FastAPI app object.
- `--reload` restarts the server automatically when backend code changes.
- `--host 127.0.0.1` makes the API available only on your machine.
- `--port 8000` serves the API at `http://127.0.0.1:8000`.

Check that the backend is running:

```bash
curl http://127.0.0.1:8000/api/health
```

Expected response:

```json
{"status":"ok"}
```

### 11.5 Frontend Setup, Command by Command

Open a second terminal and go to the frontend folder:

```bash
cd /path/to/fashion-garment-classification-inspiration-web-app/frontend
```

Purpose:

- The React app, Vite config, and frontend package files live here.

Install frontend dependencies:

```bash
npm install
```

Purpose:

- Installs React, Vite, TypeScript, and testing-related frontend packages into `frontend/node_modules`.
- Reads `frontend/package.json` and `frontend/package-lock.json`.

Start the frontend dev server:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000/api npm run dev
```

Purpose:

- Starts the Vite development server.
- `VITE_API_BASE_URL` tells the React app where the backend API is running.
- `npm run dev` runs the Vite dev command from `package.json`.
- The frontend usually opens at `http://127.0.0.1:5173`.

Open the site:

```text
http://127.0.0.1:5173/
```

You should see the upload panel, hybrid search controls, image grid, and detail panel. The status badge should say `API online` when the frontend can reach the backend.

## 12. Seed Local Demo Data

The repo includes an 80-image Pexels evaluation dataset. To import it into the app library:

```bash
DATABASE_URL=sqlite:///./backend/demo.db \
UPLOAD_STORAGE_PATH=backend/storage/uploads \
FAISS_INDEX_PATH=infra/faiss/demo.index \
OPENAI_API_KEY= \
python scripts/import_eval_dataset.py --labels eval/dataset/labels/labels.json --limit 80
```

Then start the backend with the same database and storage paths.

Why these inline variables are included:

- `DATABASE_URL=sqlite:///./backend/demo.db` tells the import script to write to a root-relative demo database.
- `UPLOAD_STORAGE_PATH=backend/storage/uploads` tells it where copied image files should go.
- `FAISS_INDEX_PATH=infra/faiss/demo.index` tells it where to write the local vector index.
- `OPENAI_API_KEY=` intentionally leaves OpenAI blank so the import uses the deterministic fallback classifier.

## 13. Refresh Pexels Images

If a Pexels API key is available:

```bash
PEXELS_API_KEY=your_pexels_key \
python eval/scripts/prepare_pexels_dataset.py --count 80 --clear-existing
```

Outputs:

- `eval/dataset/images/pexels-*.jpg`
- `eval/dataset/labels/labels.json`
- `eval/dataset/pexels_attribution.json`

No Pexels key was present in the provided Word document or local environment during implementation, so the existing checked-in Pexels dataset was used.

## 14. Build and Test

Backend tests:

```bash
cd backend
python -m pytest
```

Frontend build:

```bash
cd frontend
npm run build
```

Run evaluation:

```bash
python eval/scripts/run_eval.py \
  --labels eval/dataset/labels/labels.json \
  --output-dir eval/reports
```

## 15. How to Use the Website

1. Start backend and frontend.
2. Open `http://127.0.0.1:5173/`.
3. Upload a garment photo.
4. Wait for status to become `classified`.
5. Search with natural language, such as:
   - `red embroidered dress`
   - `streetwear jacket`
   - `artisan market`
6. Use filters for garment attributes, location/time context, designer, and annotations.
7. Select an image card to inspect AI metadata.
8. Add designer tags and notes.
9. Search again using annotation keywords or designer name.

## 16. Deployment Options

The full app needs a running backend because upload, classification, database persistence, and annotations are server-side features.

Good free or low-cost preview options:

- Render web service for the FastAPI backend.
- Render PostgreSQL for the database.
- Render static site, Netlify, or Vercel for the frontend.

Backend deploy commands:

```bash
cd backend && pip install -e .
```

```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Frontend deploy environment:

```text
VITE_API_BASE_URL=https://your-backend-url/api
```

Production caveat:

- Local file upload storage is fine for a proof of concept.
- A hosted production system should move images to S3, R2, GCS, or another persistent object store.

## 17. Why Certain Choices Were Made

### Why FastAPI?

FastAPI is lightweight, easy to test, has strong Pydantic integration, and is well suited for API-first prototypes.

### Why React and Vite?

React is familiar and flexible for interactive UI. Vite keeps setup and iteration fast.

### Why SQLAlchemy repositories?

Repositories isolate database access from services. This keeps business workflows easier to read and test.

### Why FAISS?

FAISS gives local vector similarity search without needing a managed vector database.

### Why local storage?

It keeps the proof of concept simple. The architecture still leaves room to replace local storage with cloud object storage.

### Why background tasks instead of Celery?

FastAPI background tasks are enough for this one-day proof of concept. A production system would use a durable queue.

### Why include fallback AI?

It makes the app runnable without secret keys and keeps tests deterministic.

## 18. Limitations to Say Clearly

- The fallback classifier is not a substitute for real multimodal reasoning.
- Material, occasion, consumer profile, and location can be speculative from images alone.
- Evaluation labels need manual review for stronger quality claims.
- Local file storage is not production durable.
- Background tasks are not retry-safe.
- There is no authentication or team ownership yet.
- There is no human correction workflow for AI metadata yet.

## 19. Future Improvements

- Add authentication and team workspaces.
- Store images in S3/R2/GCS.
- Add durable job processing with Celery, RQ, or a cloud queue.
- Add per-field confidence scores.
- Add prompt/model version tracking.
- Add human correction workflow.
- Use corrected metadata as evaluation labels.
- Add visual embedding search.
- Add full-text database indexes.
- Add reranking for hybrid search.
- Add observability for model latency, errors, and cost.
- Add deployment-specific storage and database configuration.

## 20. Technical Review Questions and Suggested Answers

### What problem does this solve?

Designers collect a lot of visual inspiration, but photos become hard to organize and reuse. This app turns raw images into searchable AI metadata and lets designers add human context over time.

### What is the core workflow?

Upload image, classify with AI, persist metadata, embed description, index it, show the image in a grid, search/filter, and add annotations.

### What is hybrid search here?

Hybrid search combines deterministic filters over structured fields with semantic similarity over AI-generated descriptions and text search over metadata and annotations.

### How do you prevent the AI from hallucinating?

The prompt asks the model to return `unknown` when a field cannot be visually inferred. The response is parsed against a strict schema so malformed output is rejected.

### Why did you add a local fallback classifier?

So the project can run without API keys and so tests remain deterministic. It is clearly documented as a demo fallback, not the quality path.

### How did you evaluate the model?

I prepared an 80-image Pexels dataset, defined expected labels, ran classification, calculated per-field accuracy, and wrote confusion analysis and limitations.

### What are the weakest model fields?

Material, location context, and occasion are the hardest because they often require context beyond pixels. Color can also be noisy because backgrounds and lighting influence pixels.

### What would you improve first?

Manual label review and a human correction UI. Better labels improve evaluation, and corrected metadata can become future training or prompt-evaluation data.

### How would you make it production ready?

Add authentication, cloud object storage, durable background jobs, persistent vector storage, database migrations, observability, retry/idempotency, and deployment secrets management.

### Why are annotations separate from AI metadata?

AI metadata is generated and should remain auditable. Designer annotations are human-authored and may include subjective trend notes, business context, or corrections.

### How do dynamic filters work?

The frontend reads the loaded image metadata and derives unique values for each filter. That way, filter options reflect the actual library instead of a hardcoded taxonomy.

### Why is SQLite supported if PostgreSQL is the target?

SQLite makes tests and local demos simpler. PostgreSQL remains the intended durable production database.

### What was timeboxed?

The project prioritizes the end-to-end workflow, clean boundaries, tests, evaluation pipeline, and documentation. Production infrastructure like auth, durable queues, cloud storage, and migrations is documented as future work.

## 21. Important Commands

Install backend:

```bash
cd backend
python -m pip install -e ".[test]"
```

Run backend:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Install frontend:

```bash
cd frontend
npm install
```

Run frontend:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000/api npm run dev
```

Run backend tests:

```bash
cd backend
python -m pytest
```

Build frontend:

```bash
cd frontend
npm run build
```

Run evaluation:

```bash
python eval/scripts/run_eval.py --labels eval/dataset/labels/labels.json --output-dir eval/reports
```

Import Pexels demo data:

```bash
python scripts/import_eval_dataset.py --labels eval/dataset/labels/labels.json --limit 80
```

## 22. Final Technical Review Notes

This submission is strongest as a proof of concept that demonstrates:

- End-to-end product workflow.
- Practical AI integration.
- Structured metadata design.
- Hybrid search thinking.
- Evaluation awareness.
- Clean testable backend architecture.
- Honest documentation of tradeoffs.

The main point is that the system is intentionally small but shaped so each prototype choice has a production replacement path.
