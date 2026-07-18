from langchain_qdrant import RetrievalMode

from app.services.retrieval.retriever import Retriever
from app.services.retrieval.reranker import Reranker


QUERY = "reinforcement learning policy gradient"

retriever = Retriever()

documents = retriever.retrieve(
    query=QUERY,
    mode=RetrievalMode.HYBRID,
    k=20
)

print("\nRetrieved Documents\n")

for i, doc in enumerate(documents, start=1):

    print("=" * 100)

    print(f"Rank : {i}")

    print(doc.metadata["title"])

    print(doc.page_content[:200])

reranker = Reranker()

reranked_documents = reranker.rerank(
    query=QUERY,
    documents=documents,
    top_k=5
)

print("\n\nAfter Reranking\n")

for i, doc in enumerate(reranked_documents, start=1):

    print("=" * 100)

    print(f"Rank : {i}")

    print(doc.metadata["title"])

    print(f"Score : {doc.metadata['reranker_score']:.4f}")

    print(doc.page_content[:200])

