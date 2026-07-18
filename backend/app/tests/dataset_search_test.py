from app.services.dataset.dataset_searcher import DatasetSearcher

searcher = DatasetSearcher(
    "research-papers/cs_cv_papers.jsonl"
)

results = searcher.search(
    "vision transformer",
    top_k=10
)

for paper in results:

    print(paper["title"])

    print(paper["score"])

    print()