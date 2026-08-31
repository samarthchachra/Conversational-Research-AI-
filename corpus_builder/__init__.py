# corpus_builder — Offline Research Paper Corpus Pipeline
#
# This package is entirely separate from the production FastAPI service.
# Run it locally or on a batch machine to index papers into Qdrant.
# The production API (backend/) only reads from Qdrant — it never runs
# any code from this package.
