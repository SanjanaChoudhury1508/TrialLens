import re
from app.services.embedding_service import EmbeddingService
from app.database.vector_store import VectorStore
from app.services.reranker import Reranker


class RetrievalService:
    """
    Hybrid retrieval service.

    Pipeline:
        1. Resolve trial context
        2. Build retrieval-focused query
        3. Dense vector search
        4. PostgreSQL keyword search
        5. Reciprocal Rank Fusion
        6. Source-aware candidate scoring
        7. Trial-aware filtering / boosting
        8. Cross-encoder reranking
        9. Return top-K
    """

    def __init__(self):
        self.reranker = Reranker()
        self.embedder = EmbeddingService()
        self.store = VectorStore()

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
        conversation_context: str | None = None,
    ):

        # -------------------------------------------------
        # 0. RESOLVE TRIAL CONTEXT
        # -------------------------------------------------

        trial_id = self._extract_trial_id(
            question,
            conversation_context,
        )

        trial_name = self._extract_trial_name(
            question,
            conversation_context,
        )

        retrieval_query = self._build_retrieval_query(
            question=question,
            trial_id=trial_id,
            trial_name=trial_name,
        )

        # -------------------------------------------------
        # 1. VECTOR SEARCH
        # -------------------------------------------------

        embedding = self.embedder.embed(
            retrieval_query
        )

        vector_results = self.store.search(
            embedding,
            top_k=top_k * 4,
        )

        # -------------------------------------------------
        # 2. KEYWORD SEARCH
        # -------------------------------------------------

        keyword_results = self.store.keyword_search(
            retrieval_query,
            top_k=top_k * 4,
        )

        # -------------------------------------------------
        # 3. RECIPROCAL RANK FUSION
        # -------------------------------------------------

        fused = {}

        k = 60

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
        # 4. SOURCE-AWARE + TRIAL-AWARE SCORING
        # -------------------------------------------------

        question_lower = question.lower()
        retrieval_lower = retrieval_query.lower()

        for item in fused.values():

            result = item["result"]

            document_id = (
                result.get("document_id") or ""
            ).lower()

            result_trial_id = (
                result.get("trial_id") or ""
            ).lower()

            content = (
                result.get("content") or ""
            ).lower()

            section = (
                result.get("section") or ""
            ).lower()

            source_boost = 0.0

            # ---------------------------------------------
            # EXACT TRIAL ID MATCH
            # ---------------------------------------------

            if (
                trial_id
                and result_trial_id == trial_id.lower()
            ):
                source_boost += 0.50

            # ---------------------------------------------
            # EXACT NCT ID IN CURRENT QUESTION
            # ---------------------------------------------

            if (
                result_trial_id
                and result_trial_id in question_lower
            ):
                source_boost += 0.20

            # ---------------------------------------------
            # DOCUMENT ID MENTIONED IN QUESTION
            # ---------------------------------------------

            if (
                document_id
                and document_id in question_lower
            ):
                source_boost += 0.12

            # ---------------------------------------------
            # A-BRAVE TERMINOLOGY
            # ---------------------------------------------

            if (
                trial_name
                and trial_name.lower() == "a-brave"
            ):

                if (
                    "a-brave" in content
                    or "a-brave" in section
                    or "a-brave" in document_id
                ):
                    source_boost += 0.20

                if (
                    result_trial_id
                    == "nct02926196"
                ):
                    source_boost += 0.20

            # ---------------------------------------------
            # STRONG DOMAIN TERMS
            # ---------------------------------------------

            important_terms = [
                "triple-negative",
                "tnbc",
                "avelumab",
                "high-risk",
                "early breast cancer",
                "stratum b",
                "coprimary endpoint",
                "primary endpoint",
                "overall survival",
                "disease-free survival",
                "hazard ratio",
                "invasive residual disease",
                "neoadjuvant chemotherapy",
            ]

            matched_terms = sum(
                1
                for term in important_terms
                if term in retrieval_lower
                and term in content
            )

            source_boost += (
                matched_terms * 0.03
            )

            item["source_boost"] = source_boost

            item["combined_score"] = (
                item["rrf_score"]
                + source_boost
            )

        # -------------------------------------------------
        # 5. SELECT CANDIDATES
        # -------------------------------------------------

        candidates = sorted(
            fused.values(),
            key=lambda x: x["combined_score"],
            reverse=True,
        )

        # Give the cross-encoder enough candidates.
        candidates = candidates[:top_k * 4]

        # -------------------------------------------------
        # 6. TRIAL-AWARE CANDIDATE FILTERING
        # -------------------------------------------------

        if trial_id:

            matching_trial = [
                item
                for item in candidates
                if (
                    item["result"]
                    .get("trial_id")
                    or ""
                ).lower()
                == trial_id.lower()
            ]

            # Only restrict the pool if we actually
            # found enough candidates belonging to
            # the resolved trial.
            if len(matching_trial) >= min(
                2,
                top_k,
            ):
                candidates = matching_trial

        rerank_input = [
            item["result"]
            for item in candidates
        ]

        # -------------------------------------------------
        # 7. CROSS-ENCODER RERANKING
        # -------------------------------------------------

        reranked = self.reranker.rerank(
            retrieval_query,
            rerank_input,
        )

        # -------------------------------------------------
        # 8. FINAL TRIAL-AWARE OUTPUT
        # -------------------------------------------------

        results = []

        for result in reranked:

            if trial_id:

                result_trial_id = (
                    result.get("trial_id")
                    or ""
                ).lower()

                if (
                    result_trial_id
                    and result_trial_id
                    != trial_id.lower()
                ):
                    continue

            results.append(result)

            if len(results) >= top_k:
                break

        return results

    # =====================================================
    # TRIAL CONTEXT HELPERS
    # =====================================================

    @staticmethod
    def _extract_trial_id(
        question: str,
        conversation_context: str | None = None,
    ):
        """
        Extract an NCT identifier from the current
        question first, then from conversation context.
        """

        sources = [
            question or "",
            conversation_context or "",
        ]

        pattern = re.compile(
            r"\bNCT\d{8}\b",
            re.IGNORECASE,
        )

        for text in sources:

            match = pattern.search(text)

            if match:
                return match.group(0).upper()

        return None

    @staticmethod
    def _extract_trial_name(
        question: str,
        conversation_context: str | None = None,
    ):
        """
        Extract known trial names from the current
        question or conversation context.

        This is intentionally conservative.
        """

        combined = (
            f"{question or ''} "
            f"{conversation_context or ''}"
        ).lower()

        if "a-brave" in combined:
            return "A-BRAVE"

        return None

    @staticmethod
    def _build_retrieval_query(
        question: str,
        trial_id: str | None = None,
        trial_name: str | None = None,
    ):
        """
        Builds a retrieval-focused query.

        The query contains only the current question
        plus resolved trial identity and useful retrieval
        terminology. It does NOT copy the previous answer
        into the retrieval query.
        """

        parts = []

        if trial_name:
            parts.append(trial_name)

        if trial_id:
            parts.append(trial_id)

        parts.append(question)

        question_lower = question.lower()

        # -------------------------------------------------
        # QUESTION-TYPE EXPANSION
        # -------------------------------------------------

        # Questions asking about patient populations
        # often use wording different from the source.
        if (
            "which patients" in question_lower
            or "what patients" in question_lower
            or "who was included" in question_lower
            or "who were included" in question_lower
            or "eligible patients" in question_lower
            or "eligibility" in question_lower
        ):
            parts.extend(
                [
                    "patient population",
                    "inclusion criteria",
                    "eligibility criteria",
                    "defined as",
                    "patients with",
                ]
            )

        # Endpoint questions
        if (
            "endpoint" in question_lower
            or "endpoints" in question_lower
        ):
            parts.extend(
                [
                    "primary endpoint",
                    "coprimary endpoint",
                    "secondary endpoint",
                    "outcomes",
                ]
            )

        # Hazard-ratio questions
        if (
            "hazard ratio" in question_lower
            or "hazard ratio" in question_lower
        ):
            parts.extend(
                [
                    "HR",
                    "95% CI",
                    "confidence interval",
                ]
            )

        # Stratum questions
        if "stratum" in question_lower:
            parts.extend(
                [
                    "stratum",
                    "criteria",
                    "population",
                    "invasive residual disease",
                    "neoadjuvant chemotherapy",
                ]
            )

        return " ".join(parts)

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