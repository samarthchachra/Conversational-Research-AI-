from langchain_qdrant import RetrievalMode

from app.services.retrieval.retriever import Retriever
from app.services.retrieval.reranker import Reranker
from app.services.generation.generation_service import GenerationService


query = "Explain Vision Transformer architecture."


retriever = Retriever()

docs = retriever.retrieve(
    query=query,
    mode=RetrievalMode.HYBRID,
    k=100
)


reranker = Reranker()

docs = reranker.rerank(
    query=query,
    documents=docs,
    top_k=20
)


generator = GenerationService()

response = generator.generate(
    question=query,
    documents=docs
)

print(response.content)