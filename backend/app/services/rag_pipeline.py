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

        # Retrieve evidence
        chunks = self.retriever.retrieve(
            question,
            top_k=top_k,
        )

        # Build prompt
        prompt = PromptBuilder.build(
            question,
            chunks,
        )

        # Generate answer
        answer = self.llm.generate(prompt)

        return {
            "question": question,
            "answer": answer,
            "sources": [
                chunk["document_id"]
                for chunk in chunks
            ],
        }