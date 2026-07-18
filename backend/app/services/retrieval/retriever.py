from langchain_qdrant import (
    RetrievalMode
)
from app.services.vectorstore.qdrantService import get_vector_store

class Retriever:


    def get_retriever(
        self,
        mode: RetrievalMode = RetrievalMode.HYBRID,
        k: int = 20
    ):

        vector_store = get_vector_store(
            mode
        )

        return vector_store.as_retriever(
            search_kwargs={
                "k": k
            }
        )

    ####################################################

    def retrieve(
        self,
        query: str,
        mode: RetrievalMode = RetrievalMode.HYBRID,
        k: int = 20
    ):

        retriever = self.get_retriever(
            mode=mode,
            k=k
        )

        return retriever.invoke(query)