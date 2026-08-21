from app.services.embedding_service import EmbeddingService
from app.database.vector_store import VectorStore
from app.services.reranker import Reranker


class RetrievalService:
    """
    Hybrid retrieval service.

    Pipeline:

        1. Dense vector similarity search
        2. PostgreSQL keyword search
        3. Reciprocal Rank Fusion (RRF)
        4. Cross-encoder reranking
        5. Return final top-k results
    """

    def __init__(self):

        self.reranker = Reranker()
        self.embedder = EmbeddingService()
        self.store = VectorStore()

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
    ):

        # -------------------------------------------------
        # Number of candidates retrieved BEFORE reranking
        # -------------------------------------------------

        candidate_k = max(top_k * 4, 20)

        # -------------------------------------------------
        # 1. VECTOR SEARCH
        # -------------------------------------------------

        embedding = self.embedder.embed(question)

        vector_results = self.store.search(
            embedding,
            top_k=candidate_k,
        )

        # -------------------------------------------------
        # 2. KEYWORD SEARCH
        # -------------------------------------------------

        keyword_results = self.store.keyword_search(
            question,
            top_k=candidate_k,
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
        # 4. SORT BY RRF SCORE
        # -------------------------------------------------

        ranked = sorted(
            fused.values(),
            key=lambda x: x["rrf_score"],
            reverse=True,
        )

        # -------------------------------------------------
        # 5. BUILD RERANKING CANDIDATES
        # -------------------------------------------------

        candidates = []

        for item in ranked[:candidate_k]:

            result = item["result"].copy()

            result["rrf_score"] = item["rrf_score"]

            candidates.append(result)

        # -------------------------------------------------
        # 6. CROSS-ENCODER RERANKING
        # -------------------------------------------------

        reranked = self.reranker.rerank(
            question=question,
            results=candidates,
            top_k=top_k,
        )

        # -------------------------------------------------
        # 7. RETURN FINAL RESULTS
        # -------------------------------------------------

        return reranked

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