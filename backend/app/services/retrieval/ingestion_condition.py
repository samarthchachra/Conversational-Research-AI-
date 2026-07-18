class ingestionCondition:

    def __init__(
        self,
        threshold: float = 0.65
    ):
        self.threshold = threshold



    def should_ingest(
        self,
        documents: list
    ):

        if len(documents) == 0:
            return True

        best_score = documents[0].metadata.get(
            "reranker_score",
            0.0
        )

        print(
            f"Best Reranker Score : {best_score:.4f}"
        )

        return best_score < self.threshold