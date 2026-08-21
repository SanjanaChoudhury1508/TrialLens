from sentence_transformers import CrossEncoder


class Reranker:
    """
    Reranks retrieved documents using a cross-encoder.

    The retriever finds candidate documents using vector/keyword
    similarity. The reranker then evaluates the relationship
    between the question and each candidate directly.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):

        self.model_name = model_name

        print(f"Loading reranker: {model_name}")

        self.model = CrossEncoder(model_name)

        print("✓ Reranker loaded")

    def rerank(
        self,
        question: str,
        results: list[dict],
        top_k: int = 5,
    ) -> list[dict]:

        if not results:
            return []

        # Create question-document pairs
        pairs = [
            (
                question,
                result.get("content", "")
            )
            for result in results
        ]

        # Generate relevance scores
        scores = self.model.predict(pairs)

        # Attach scores
        reranked = []

        for result, score in zip(results, scores):

            item = dict(result)

            item["rerank_score"] = float(score)

            reranked.append(item)

        # Highest relevance first
        reranked.sort(
            key=lambda x: x["rerank_score"],
            reverse=True,
        )

        return reranked[:top_k]