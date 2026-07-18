from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-base"
    ):

        self.model = CrossEncoder(
            model_name,
            trust_remote_code=True
        )
        

    def rerank(
        self,
        query: str,
        documents: list,
        top_k: int = 5
    ):

        pairs = [
            (query, doc.page_content)
            for doc in documents
        ]

        scores = self.model.predict(
            pairs
        )

        ranked = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True
        )

        reranked_documents = []

        for doc, score in ranked[:top_k]:

            doc.metadata["reranker_score"] = float(score)

            reranked_documents.append(doc)
            

        return reranked_documents