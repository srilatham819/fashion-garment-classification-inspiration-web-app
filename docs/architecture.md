# Architecture Notes

This document will capture implementation decisions as the system evolves.

## Target Components

- FastAPI backend for upload, metadata, classification orchestration, search, and annotations.
- PostgreSQL metadata store for images, structured AI attributes, annotations, and evaluation runs.
- FAISS index for local vector search over descriptions and annotations.
- OpenAI vision integration for multimodal image classification.
- React frontend for upload, visual library browsing, filtering, search, and annotation workflows.
- Evaluation pipeline for labeled fashion image test sets and per-attribute metrics.

