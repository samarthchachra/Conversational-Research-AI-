import os
import glob
import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class DatasetSearcher:

    def __init__(self, dataset_directory: str):

        self.records = []

        corpus = []

        json_files = sorted(
            glob.glob(
                os.path.join(
                    dataset_directory,
                    "*.jsonl"
                )
            )
        )

        if len(json_files) == 0:
            raise FileNotFoundError(
                f"No jsonl files found in {dataset_directory}"
            )

        print(f"\nFound {len(json_files)} dataset files.\n")

        total_records = 0
        seen_ids=set()
        for file in json_files:

            print(
                f"Loading {os.path.basename(file)}..."
            )

            file_records = 0

            with open(
                file,
                "r",
                encoding="utf-8"
            ) as f:
                
                for line in f:
                
                    record = json.loads(line)
                    if record["id"] in seen_ids:
                        continue
                    seen_ids.add(record['id'])
                    self.records.append(record)

                    corpus.append(
                        f"{record.get('title', '')} "
                        f"{record.get('abstract', '')}"
                    )

                    file_records += 1

            total_records += file_records

            print(
                f"Loaded {file_records} papers."
            )

        print(
            f"\nTotal Papers Indexed : {total_records}"
        )

        print("\nBuilding TF-IDF Index...\n")

        self.vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        self.document_matrix = (
            self.vectorizer.fit_transform(
                corpus
            )
        )

        print("TF-IDF Index Ready.\n")

    ########################################################

    def search(
        self,
        query: str,
        top_k: int = 20
    ):

        query_vector = self.vectorizer.transform(
            [query]
        )

        similarities = cosine_similarity(
            query_vector,
            self.document_matrix
        )[0]

        ranked_indices = (
            similarities.argsort()[::-1][:top_k]
        )

        results = []

        for idx in ranked_indices:

            paper = self.records[idx].copy()

            paper["score"] = float(
                similarities[idx]
            )

            results.append(paper)

        return results