# Fashion Inspiration AI

Fashion Inspiration AI is a lightweight full-stack system for organizing field-captured fashion imagery. Designers can upload garment photos, classify them with a multimodal AI model, store structured fashion metadata, and retrieve inspiration through hybrid search that combines SQL filters with semantic vector similarity.

The implementation is intentionally proof-of-concept sized, but the architecture is shaped like a production service: thin API routes, explicit service boundaries, repository-based persistence, strict model output validation, and a rerunnable evaluation pipeline.

## Architecture

```text
React frontend
  |
  | upload, browse, search, annotate
  v
FastAPI backend
  |
  +-- API routes
  |     images, classify, search, annotations
  |
  +-- Application services
  |     upload orchestration
  |     AI classification
  |     semantic indexing
  |     hybrid search
  |
  +-- Repositories
  |     image metadata
  |     AI metadata
  |     embedding references
  |
  +-- Adapters
        OpenAI vision + embeddings
        local image storage
        FAISS vector index
        PostgreSQL metadata store
```

### Backend

The backend is a FastAPI application under `backend/app`.

- `api/routes/` contains thin HTTP handlers.
- `api/dependencies.py` wires services and repositories through FastAPI dependency injection.
- `services/` contains application use cases such as upload, classification, semantic indexing, and hybrid search.
- `repositories/` isolates SQLAlchemy persistence from business workflows.
- `models/` defines database tables for images, AI metadata, annotations, and embedding references.
- `vector/faiss_index.py` owns local FAISS vector storage.
- `storage/local.py` owns local image persistence.
- `workers/classification_tasks.py` contains the background classification entrypoint.

### Data Model

The current metadata store includes:

- `images`: original filename, local path, MIME type, processing status, and error state.
- `ai_metadata`: structured classification fields, natural-language description, raw model output, and model name.
- `user_annotations`: designer notes, tags, author, and timestamps.
- `embedding_references`: mapping between image records and vector IDs stored in FAISS.

PostgreSQL is the target database. SQLite-compatible session setup is kept to make tests and local development easier.

## AI Pipeline

The image classification flow is:

1. A designer uploads an image through `POST /api/images`.
2. The backend validates file type and size.
3. The image is saved locally.
4. An `images` row is created with status `pending`.
5. A background task starts classification.
6. The classification service marks the image `processing`.
7. The OpenAI vision adapter sends the image to a multimodal model.
8. The response is parsed against a strict JSON schema.
9. Structured AI metadata is persisted.
10. The natural-language description is embedded.
11. The embedding is written to FAISS and linked back through `embedding_references`.
12. The image is marked `classified`, or `failed` with an error message.

The strict model response includes:

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

The prompt asks the model to return `unknown` when a field cannot be visually inferred. This is important for interview-quality GenAI work: the system should not invent material, location, or merchandising context when the image does not support it.

## Search

The system supports hybrid retrieval:

1. Structured SQL filtering over fields such as garment type, style, material, occasion, and location context.
2. Semantic similarity search over AI-generated descriptions using embeddings and FAISS.

For a query such as:

```text
red festive embroidered dress
```

the backend can rank visually similar descriptions semantically, then intersect those results with structured filters such as `garment_type=dress` or `occasion=festival`.

This design keeps deterministic filters explainable while allowing natural-language discovery across richer descriptions.

## Evaluation

The evaluation pipeline lives in `eval/scripts/run_eval.py`.

Dataset preparation options:

- `eval/scripts/prepare_pexels_dataset.py` downloads 50-100 fashion photos from the official Pexels API. Set `PEXELS_API_KEY` first. Pexels API documentation requires an API key in the `Authorization` header, and Pexels asks API users to link back/credit photographers where possible.
- `eval/scripts/prepare_fashion_mnist_dataset.py` downloads a reproducible 100-image open-source Fashion-MNIST garment test set from Zalando Research.
- `eval/scripts/prepare_wikimedia_dataset.py` prepares a Wikimedia Commons starter set and marks labels for manual review.

Example Pexels run:

```bash
PEXELS_API_KEY=your_key .venv312/bin/python eval/scripts/prepare_pexels_dataset.py --count 80 --clear-existing
.venv312/bin/python eval/scripts/run_eval.py --labels eval/dataset/labels/labels.json --output-dir eval/reports
```

Expected label format:

```json
[
  {
    "image_path": "eval/dataset/images/example.jpg",
    "mime_type": "image/jpeg",
    "expected": {
      "garment_type": "dress",
      "style": "festive",
      "material": "cotton",
      "color_palette": ["red"],
      "pattern": "embroidered",
      "season": "fall/winter",
      "occasion": "celebration",
      "consumer_profile": "occasionwear customer",
      "trend_notes": "embroidered neckline",
      "location_context": "unknown"
    }
  }
]
```

The evaluator:

- loads a labeled dataset,
- runs AI classification for each image,
- compares predictions against expected labels,
- calculates per-field accuracy,
- records confusion analysis,
- writes `eval_report.json`,
- writes a human-readable `eval_summary.md`.

The goal is not only to produce a score. The goal is to make model behavior discussable: which attributes are reliable, which are subjective, and where prompt or schema changes improve quality.

The current generated report uses 100 Fashion-MNIST images. It is useful for garment-type regression testing, but it is intentionally weak for material, occasion, color, and location evaluation because Fashion-MNIST is grayscale and has no scene context. A stronger final submission should replace or supplement it with manually reviewed street-fashion photos.

## Testing

The backend test structure covers the core risk areas:

- JSON parsing and schema validation.
- Upload flow.
- Structured search filters.
- Semantic retrieval.
- Hybrid search behavior.

The semantic tests use a deterministic hash embedding client so they do not require OpenAI network calls.

## Tradeoffs

This project optimizes for a credible one-day proof of concept rather than full production depth.

Chosen tradeoffs:

- Local filesystem storage instead of S3/R2.
- FastAPI background tasks instead of Celery, Redis Queue, or a durable job system.
- FAISS local index instead of a managed vector database.
- SQLAlchemy repositories without a full unit-of-work abstraction.
- Strict JSON schema validation, but no human review workflow yet.
- PostgreSQL target, with SQLite-friendly test behavior.
- Simple semantic ranking rather than advanced reranking.

These tradeoffs keep setup small while preserving a clean path to production.

## Future Improvements

Production hardening:

- Replace FastAPI background tasks with a durable queue.
- Move image storage to S3, R2, or GCS.
- Add authentication, designer/team ownership, and row-level authorization.
- Add database migrations for all model changes.
- Add observability around model latency, token usage, failures, and retry rates.
- Add idempotent classification jobs and safe reclassification.

AI quality:

- Add confidence/uncertainty fields per attribute.
- Track prompt version and model version in a first-class table.
- Add human correction UI and use corrections as future eval data.
- Split visually grounded attributes from speculative merchandising attributes.
- Improve material and occasion classification with domain-specific examples.
- Add batch evaluation across multiple model/prompt versions.

Search quality:

- Add full-text search alongside semantic search.
- Add image similarity search using visual embeddings.
- Add reranking for hybrid results.
- Support faceted filters generated dynamically from metadata.
- Add explainability for why each result matched.

Frontend:

- Build the upload, grid, detail drawer, filters, annotation UI, and evaluation report views.
- Add loading, pending, failed, and reclassify states.
- Clearly distinguish AI-generated metadata from designer annotations.

## Current Status

The backend implementation includes upload, classification service wiring, strict JSON parsing, metadata persistence, semantic indexing, hybrid search, and evaluation scaffolding. The frontend is currently scaffolded but not functionally implemented.
