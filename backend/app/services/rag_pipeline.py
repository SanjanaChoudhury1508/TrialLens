from app.services.retrieval_service import RetrievalService
from app.services.prompt_builder import PromptBuilder
from app.services.llm_service import LLMService

import re


class RAGPipeline:

    def __init__(self):

        self.retriever = RetrievalService()
        self.llm = LLMService()

    @staticmethod
    def _extract_trial_id(conversation_context: str | None):
        """
        Extract an NCT trial ID from previous conversation context.
        """

        if not conversation_context:
            return None

        match = re.search(
            r"\bNCT\d{8}\b",
            conversation_context,
            re.IGNORECASE,
        )

        if match:
            return match.group(0).upper()

        return None

    def ask(
        self,
        question: str,
        top_k: int = 5,
        conversation_context: str | None = None,
    ):

        # -------------------------------------------------
        # 1. RETRIEVE HYBRID + RERANKED EVIDENCE
        # -------------------------------------------------

        retrieval_query = question.strip()

        # If this is a follow-up question, use the previous
        # trial identity to make retrieval more precise.
        trial_id = self._extract_trial_id(
            conversation_context
        )

        if trial_id:
            retrieval_query = (
                f"{question.strip()} "
                f"Clinical trial {trial_id}"
            )

        chunks = self.retriever.retrieve(
            retrieval_query,
            top_k=top_k,
        )

        # -------------------------------------------------
        # 2. BUILD PROMPT
        # -------------------------------------------------

        prompt = PromptBuilder.build(
            question,
            chunks,
            conversation_context=conversation_context,
        )

        # -------------------------------------------------
        # 3. GENERATE ANSWER
        # -------------------------------------------------

        answer = self.llm.generate(prompt)

        # -------------------------------------------------
        # 4. BUILD UNIQUE SOURCES
        # -------------------------------------------------

        sources = []

        seen = set()

        for chunk in chunks:

            document_id = chunk.get("document_id")
            trial_id = chunk.get("trial_id")
            source_type = chunk.get("source_type")
            section = chunk.get("section")
            content = chunk.get("content")
            rerank_score = chunk.get("rerank_score")

            key = (
                document_id,
                section,
                content,
            )

            if key in seen:
                continue

            seen.add(key)

            sources.append(
                {
                    "document_id": document_id,
                    "trial_id": trial_id,
                    "source_type": source_type,
                    "section": section,
                    "content": content,
                    "relevance_score": rerank_score,
                }
            )

        # -------------------------------------------------
        # 5. RETURN RESULT
        # -------------------------------------------------

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
        }