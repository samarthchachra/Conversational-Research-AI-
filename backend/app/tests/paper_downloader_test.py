from app.services.dataset.dataset_searcher import DatasetSearcher
from app.services.dataset.paper_downloader import PaperDownloader


searcher = DatasetSearcher(
    "research-papers/cs_cv_papers.jsonl"
)

papers = searcher.search(
    query="vision transformer",
    top_k=5
)

downloader = PaperDownloader(
    "papers"
)

downloaded = downloader.download_papers(
    papers
)

print(downloaded)