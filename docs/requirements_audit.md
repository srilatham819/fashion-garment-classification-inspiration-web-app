# Requirements Audit

Source document: `fashion_case_study_one_pager.docx`

## Summary

The project satisfies the requested proof-of-concept scope for a local full-stack submission. It includes upload, AI classification, structured metadata storage, hybrid search, dynamic filters, designer annotations, an 80-image Pexels evaluation dataset, model evaluation reports, and automated tests.

## Requirement Coverage

| Requirement | Status | Notes |
| --- | --- | --- |
| Web app for fashion designers | Complete | React frontend with upload, library grid, filters, detail panel, and annotations. |
| Upload garment photos | Complete | `POST /api/images` saves files locally and starts classification. |
| Multimodal AI classification | Complete | Uses OpenAI when `OPENAI_API_KEY` is set; includes deterministic local fallback for demos/tests. |
| Natural-language description | Complete | Stored in `ai_metadata.description`. |
| Structured attributes | Complete | Garment type, style, material, colors, pattern, season, occasion, consumer profile, trend notes, and location context. |
| Store AI metadata | Complete | SQLAlchemy models persist images, metadata, annotations, and embedding references. |
| Visual image grid | Complete | Frontend displays uploaded/imported library images. |
| Attribute filters | Complete | Filters garment type, style, material, color, pattern, season, occasion, consumer profile, trend notes through query text, and location context. |
| Context filters | Complete | Supports continent, country, city, year, month, season, and designer. Location facets are derived from location text formatted like `Asia > India > Mumbai`. |
| Dynamic filters | Complete | Frontend facets are generated from loaded library data. |
| Full-text search | Complete | Searches descriptions, trend notes, structured fields, location context, and annotation text/tags. |
| Designer annotations | Complete | Designers can add tags and notes; annotation author supports designer filtering. |
| Annotations clearly distinguished | Complete | Detail panel separates `AI Metadata` and `Designer Annotations`. |
| Evaluation set of 50-100 images | Complete | 80 Pexels images are included under `eval/dataset/images`. |
| Expected attributes and accuracy report | Complete with caveat | Labels and reports exist. Labels are query-derived and marked for manual review, which is documented as a limitation. |
| Unit parsing test | Complete | `backend/tests/unit/test_json_parsing.py`. |
| Integration filter test | Complete | `backend/tests/integration/test_search_filters.py`, including location/time/designer/annotation behavior. |
| End-to-end upload/classify/filter test | Complete | `backend/tests/e2e/test_upload_classify_filter.py`. |
| Clear README and architecture notes | Complete | README plus detailed docs in `docs/`. |
| GitHub repository | Ready | Local commit can be pushed once a GitHub repo exists or credentials are available. |

## Known Limitations

- Pexels images are already present, but a fresh Pexels download requires `PEXELS_API_KEY`. No key was present in the provided document or local environment.
- The local fallback classifier is intentionally simple. For real multimodal garment reasoning, set `OPENAI_API_KEY`.
- GitHub Pages can only host the static frontend demo. Upload, classification, and persistent annotations need a running backend.
- Evaluation labels are starter labels derived from Pexels query buckets; a production-grade evaluation should manually review every label.

