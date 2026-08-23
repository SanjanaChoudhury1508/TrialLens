from app.services.embedding_service import EmbeddingService
from app.database.vector_store import VectorStore
from app.services.reranker import Reranker


class RetrievalService:
    """
    Hybrid retrieval service.

    Pipeline:
        1. Dense vector search
        2. PostgreSQL keyword search
        3. Reciprocal Rank Fusion
        4. Source-aware candidate scoring
        5. Cross-encoder reranking
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
        # 1. VECTOR SEARCH
        # -------------------------------------------------

        embedding = self.embedder.embed(question)

        vector_results = self.store.search(
            embedding,
            top_k=top_k * 4,
        )

        # -------------------------------------------------
        # 2. KEYWORD SEARCH
        # -------------------------------------------------

        keyword_results = self.store.keyword_search(
            question,
            top_k=top_k * 4,
        )

        # -------------------------------------------------
        # 3. RECIPROCAL RANK FUSION
        # -------------------------------------------------

        fused = {}

        k = 60

        for rank, result in enumerate(vector_results, start=1):

            chunk_id = self._chunk_key(result)

            if chunk_id not in fused:
                fused[chunk_id] = {
                    "result": result,
                    "rrf_score": 0.0,
                }

            fused[chunk_id]["rrf_score"] += 1 / (k + rank)

        for rank, result in enumerate(keyword_results, start=1):

            chunk_id = self._chunk_key(result)

            if chunk_id not in fused:
                fused[chunk_id] = {
                    "result": result,
                    "rrf_score": 0.0,
                }

            fused[chunk_id]["rrf_score"] += 1 / (k + rank)

        # -------------------------------------------------
        # 4. SOURCE-AWARE SCORING
        # -------------------------------------------------

        question_lower = question.lower()

        for item in fused.values():

            result = item["result"]

            document_id = (
                result.get("document_id") or ""
            ).lower()

            trial_id = (
                result.get("trial_id") or ""
            ).lower()

            content = (
                result.get("content") or ""
            ).lower()

            section = (
                result.get("section") or ""
            ).lower()

            source_boost = 0.0

            # Exact NCT ID mentioned in the question
            if trial_id and trial_id in question_lower:
                source_boost += 0.15

            # Document ID mentioned in the question
            if document_id and document_id in question_lower:
                source_boost += 0.12

            # Important A-BRAVE terminology
            if "a-brave" in question_lower:
                if "a-brave" in content or "a-brave" in section:
                    source_boost += 0.15

                if trial_id == "nct02926196":
                    source_boost += 0.15

            # Strong disease/trial terminology
            important_terms = [
                "triple-negative",
                "tnbc",
                "avelumab",
                "high-risk",
                "early breast cancer",
            ]

            matched_terms = sum(
                1
                for term in important_terms
                if term in question_lower
                and term in content
            )

            source_boost += matched_terms * 0.02

            item["source_boost"] = source_boost

            item["combined_score"] = (
                item["rrf_score"]
                + source_boost
            )

        # -------------------------------------------------
        # 5. SELECT CANDIDATES FOR RERANKING
        # -------------------------------------------------

        candidates = sorted(
            fused.values(),
            key=lambda x: x["combined_score"],
            reverse=True,
        )

        # Give the cross-encoder enough candidates
        candidates = candidates[:top_k * 4]

        rerank_input = [
            item["result"]
            for item in candidates
        ]

        # -------------------------------------------------
        # 6. CROSS-ENCODER RERANKING
        # -------------------------------------------------

        reranked = self.reranker.rerank(
            question,
            rerank_input,
        )

        # -------------------------------------------------
        # 7. RETURN TOP-K
        # -------------------------------------------------

        results = []

        for result in reranked[:top_k]:

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