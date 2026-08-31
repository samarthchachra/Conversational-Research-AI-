"""Dataset search module for the offline corpus builder.

Loads one or more *.jsonl research-paper dataset files from DATASET_DIR,
builds a TF-IDF index over title + abstract, and supports keyword search
to discover relevant paper metadata for a given query.

This module is intentionally self-contained and has NO dependency on the
backend/ production app. It is only run during offline corpus-building.
"""

from __future__ import annotations

import os
import glob
import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class DatasetSearcher:
    """TF-IDF search over a directory of JSONL research-paper files.

    Each JSONL file is expected to contain one JSON record per line with at
    minimum these fields:
        id, title, abstract, authors, published, categories,
        primary_category, pdf_url
    """

    def __init__(self, dataset_directory: str):

        self.records: list[dict] = []

        corpus: list[str] = []

        json_files = sorted(
            glob.glob(
                os.path.join(dataset_directory, "*.jsonl")
            )
        )

        if not json_files:
            raise FileNotFoundError(
                f"No *.jsonl files found in '{dataset_directory}'. "
                "Set DATASET_DIR to the directory containing your dataset files."
            )

        print(f"\nFound {len(json_files)} dataset file(s).\n")

        seen_ids: set[str] = set()
        total_records = 0

        for file in json_files:

            print(f"Loading {os.path.basename(file)}...")

            file_records = 0

            with open(file, "r", encoding="utf-8") as f:

                for line in f:

                    record = json.loads(line)

                    if record["id"] in seen_ids:
                        continue

                    seen_ids.add(record["id"])
                    self.records.append(record)

                    corpus.append(
                        f"{record.get('title', '')} "
                        f"{record.get('abstract', '')}"
                    )

                    file_records += 1

            total_records += file_records
            print(f"Loaded {file_records} papers.")

        print(f"\nTotal unique papers indexed: {total_records}")
        print("\nBuilding TF-IDF index...\n")

        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.document_matrix = self.vectorizer.fit_transform(corpus)

        print("TF-IDF index ready.\n")

    # -----------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 20
    ) -> list[dict]:
        """Return the top-k most relevant paper records for the query."""

        query_vector = self.vectorizer.transform([query])

        similarities = cosine_similarity(
            query_vector,
            self.document_matrix
        )[0]

        ranked_indices = similarities.argsort()[::-1][:top_k]

        results = []

        for idx in ranked_indices:

            paper = self.records[idx].copy()
            paper["score"] = float(similarities[idx])
            results.append(paper)

        return results
