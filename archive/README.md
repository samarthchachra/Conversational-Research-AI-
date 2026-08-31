# Archive — Legacy / Dead Code

This directory contains files that were removed from the active codebase during
the corpus builder / production API refactoring (August 2026).

These files are preserved here for reference. They are NOT imported by anything
in the active codebase and should NOT be moved back without reviewing the
architectural separation described in the project README.

## Contents

### `extra/`
Legacy one-off service files from early prototyping:

| File | Why archived |
|---|---|
| `embeddingService.py` | Module-level `SentenceTransformer` load. Superseded by `backend/app/services/vectorstore/embeddingService.py` (lazy init). Uses old model name `BAAI/bge-base-en` (not v1.5). |
| `pdfService.py` | Superseded by `corpus_builder/ingestion/`. |
| `vectorStoreService.py` | FAISS-based store. Project moved to Qdrant. |

### `utils/`
Early utility functions with broken/relative imports:

| File | Why archived |
|---|---|
| `pdfProcessing.py` | Uses `from utils.textProcessing import ...` — broken in package context. Logic now lives in `corpus_builder/processing/`. |
| `textProcessing.py` | Superseded by `corpus_builder/processing/`. |
| `constants.py` | Only referenced by orphaned `test_pipeline.py`. |

### `services_data/`
API client services never integrated into the active request path:

| File | Why archived |
|---|---|
| `openalexService.py` | Contains broken import `from utils.pdfProcessing import ingest_pdf`. Not imported by any active module. |
| `arxivService.py` | Not imported by any active module. Can be re-integrated into `corpus_builder/dataset/` if ArXiv live-search is needed. |
