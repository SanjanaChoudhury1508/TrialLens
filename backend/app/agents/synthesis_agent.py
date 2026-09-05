from app.agents.state import TrialLensState
from app.services.llm_service import LLMService
from app.services.prompt_builder import PromptBuilder


class SynthesisAgent:
    def __init__(self):
        self.llm = LLMService()

    def run(self, state: TrialLensState) -> TrialLensState:
        question = state["question"]
        evidence = state.get("evidence", [])
        conversation_context = state.get("conversation_context")

        try:
            prompt = PromptBuilder.build(
                question,
                evidence,
                conversation_context=conversation_context,
            )

            answer = self.llm.generate(prompt)

            return {
                "draft_answer": answer,
                "execution_trace": ["synthesis_agent"],
            }

        except Exception as exc:
            return {
                "draft_answer": "",
                "errors": [f"Synthesis agent error: {exc}"],
                "execution_trace": ["synthesis_agent:error"],
            }


synthesis_agent = SynthesisAgent()