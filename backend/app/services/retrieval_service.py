from app.services.embedding_service import EmbeddingService
from app.database.vector_store import VectorStore


class RetrievalService:
    """
    Hybrid retrieval service.

    Combines:
        1. Dense vector similarity search
        2. PostgreSQL keyword search

    using Reciprocal Rank Fusion (RRF).
    """

    def __init__(self):

        self.embedder = EmbeddingService()
        self.store = VectorStore()

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
    ):

        # -------------------------------------------------
        # 1. VECTOR SEARCH
        # -------------------------------------------------

        embedding = self.embedder.embed(question)

        vector_results = self.store.search(
            embedding,
            top_k=top_k * 2,
        )

        # -------------------------------------------------
        # 2. KEYWORD SEARCH
        # -------------------------------------------------

        keyword_results = self.store.keyword_search(
            question,
            top_k=top_k * 2,
        )

        # -------------------------------------------------
        # 3. RECIPROCAL RANK FUSION
        # -------------------------------------------------

        fused = {}

        k = 60

        # Vector ranking
        for rank, result in enumerate(
            vector_results,
            start=1,
        ):

            chunk_id = self._chunk_key(result)

            if chunk_id not in fused:

                fused[chunk_id] = {
                    "result": result,
                    "rrf_score": 0.0,
                }

            fused[chunk_id]["rrf_score"] += (
                1 / (k + rank)
            )

        # Keyword ranking
        for rank, result in enumerate(
            keyword_results,
            start=1,
        ):

            chunk_id = self._chunk_key(result)

            if chunk_id not in fused:

                fused[chunk_id] = {
                    "result": result,
                    "rrf_score": 0.0,
                }

            fused[chunk_id]["rrf_score"] += (
                1 / (k + rank)
            )

        # -------------------------------------------------
        # 4. SORT BY FUSED SCORE
        # -------------------------------------------------

        ranked = sorted(
            fused.values(),
            key=lambda x: x["rrf_score"],
            reverse=True,
        )

        # -------------------------------------------------
        # 5. RETURN TOP-K
        # -------------------------------------------------

        results = []

        for item in ranked[:top_k]:

            result = item["result"].copy()

            result["rrf_score"] = item["rrf_score"]

            results.append(result)

        return results

    @staticmethod
    def _chunk_key(result):
        """
        Creates a stable identifier for a retrieved chunk.
        """

        return (
            result["document_id"],
            result["section"],
            result["content"],
        )