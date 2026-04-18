# Setup, Usage, Build, and Test Guide

## Prerequisites

- Python 3.11 or newer.
- Node.js 20 or newer.
- Docker Desktop, if you want PostgreSQL via `docker-compose`.
- Optional: `OPENAI_API_KEY` for real multimodal classification.
- Optional: `PEXELS_API_KEY` to refresh the evaluation dataset from Pexels.

## Local Backend Setup

From the repository root:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
```

For a minimal SQLite demo:

```bash
export DATABASE_URL=sqlite:///./demo.db
export UPLOAD_STORAGE_PATH=storage/uploads
export FAISS_INDEX_PATH=../infra/faiss/demo.index
export DEMO_AI_FALLBACK=true
```

For OpenAI-backed classification:

```bash
export OPENAI_API_KEY=your_openai_key
```

Start the backend:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/api/health
```

## Local Frontend Setup

In a second terminal:

```bash
cd frontend
npm install
VITE_API_BASE_URL=http://127.0.0.1:8000/api npm run dev
```

Open:

```text
http://127.0.0.1:5173/
```

## Seed the App With Pexels Evaluation Images

The repo includes 80 Pexels images and labels. To import them into the local app library:

```bash
DATABASE_URL=sqlite:///./backend/demo.db \
UPLOAD_STORAGE_PATH=backend/storage/uploads \
FAISS_INDEX_PATH=infra/faiss/demo.index \
OPENAI_API_KEY= \
python scripts/import_eval_dataset.py --labels eval/dataset/labels/labels.json --limit 80
```

Then start the backend with the same `DATABASE_URL`, `UPLOAD_STORAGE_PATH`, and `FAISS_INDEX_PATH`.

## Refresh Pexels Dataset

Set your key and download 80 images:

```bash
PEXELS_API_KEY=your_pexels_key \
python eval/scripts/prepare_pexels_dataset.py --count 80 --clear-existing
```

This writes:

- `eval/dataset/images/pexels-*.jpg`
- `eval/dataset/labels/labels.json`
- `eval/dataset/pexels_attribution.json`

## Run Evaluation

```bash
python eval/scripts/run_eval.py \
  --labels eval/dataset/labels/labels.json \
  --output-dir eval/reports
```

Outputs:

- `eval/reports/eval_report.json`
- `eval/reports/eval_summary.md`

## Run Tests

Backend tests:

```bash
cd backend
python -m pytest
```

Frontend production build:

```bash
cd frontend
npm run build
```

End-to-end browser test is available through Playwright config:

```bash
npm run test:e2e
```

## How to Use the Website

1. Open the frontend URL.
2. Upload a garment photo.
3. Wait for the status to become `classified`.
4. Use the natural-language search box for phrases such as `red embroidered dress` or `artisan market`.
5. Use dynamic filters for garment type, style, material, color, pattern, season, occasion, consumer profile, location, year, month, designer, and annotations.
6. Select an image card to inspect AI metadata.
7. Add designer tags and notes in the detail panel.
8. Search again using annotation keywords or filter by designer.

## Environment Variables

| Variable | Purpose | Default |
| --- | --- | --- |
| `DATABASE_URL` | SQLAlchemy database URL | PostgreSQL local URL |
| `OPENAI_API_KEY` | Enables OpenAI vision and embeddings | empty |
| `OPENAI_VISION_MODEL` | Vision model name | `gpt-5.4-mini` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model name | `text-embedding-3-small` |
| `FAISS_INDEX_PATH` | Local FAISS index path | `infra/faiss/fashion.index` |
| `UPLOAD_STORAGE_PATH` | Uploaded image storage path | `backend/storage/uploads` |
| `DEMO_AI_FALLBACK` | Enables local fallback classifier | `true` |
| `VITE_API_BASE_URL` | Frontend API URL | `http://127.0.0.1:8000/api` |
| `VITE_STATIC_DEMO` | Builds a static browser-only demo | `false` |

