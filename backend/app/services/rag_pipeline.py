from app.services.retrieval_service import RetrievalService
from app.services.prompt_builder import PromptBuilder
from app.services.llm_service import LLMService


class RAGPipeline:

    def __init__(self):

        self.retriever = RetrievalService()
        self.llm = LLMService()

    def ask(
        self,
        question: str,
        top_k: int = 5,
    ):

        # -------------------------------------------------
        # 1. RETRIEVE HYBRID EVIDENCE
        # -------------------------------------------------

        chunks = self.retriever.retrieve(
            question,
            top_k=top_k,
        )

        # -------------------------------------------------
        # 2. BUILD PROMPT
        # -------------------------------------------------

        prompt = PromptBuilder.build(
            question,
            chunks,
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

            document_id = chunk.get(
                "document_id"
            )

            trial_id = chunk.get(
                "trial_id"
            )

            source_type = chunk.get(
                "source_type"
            )

            key = (
                document_id,
                trial_id,
            )

            if key in seen:
                continue

            seen.add(key)

            sources.append(
                {
                    "document_id": document_id,
                    "trial_id": trial_id,
                    "source_type": source_type,
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