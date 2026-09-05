from app.agents.state import TrialLensState
from app.services.retrieval_service import RetrievalService


class RetrieverAgent:
    def __init__(self):
        self.retriever = RetrievalService()

    def run(self, state: TrialLensState) -> TrialLensState:
        question = state["question"]
        context = state.get("conversation_context")

        try:
            documents = self.retriever.retrieve(
                question,
                top_k=5,
                conversation_context=context,
            )

            return {
                "retrieved_documents": documents,
                "execution_trace": ["retriever_agent"],
            }

        except Exception as exc:
            return {
                "retrieved_documents": [],
                "errors": state.get("errors", [])
                + [f"Retriever agent error: {exc}"],
                "execution_trace": ["retriever_agent:error"],
            }


retriever_agent = RetrieverAgent()