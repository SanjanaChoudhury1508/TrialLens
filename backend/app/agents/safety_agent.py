from app.agents.state import TrialLensState
from app.services.faers_api import FAERSService


class SafetySignalAgent:

    def __init__(self):
        self.faers = FAERSService()

    def _extract_drug(self, question: str):

        known_drugs = [
            "avelumab",
            "pembrolizumab",
            "nivolumab",
            "atezolizumab",
            "durvalumab",
            "ipilimumab",
        ]

        question_lower = question.lower()

        for drug in known_drugs:
            if drug in question_lower:
                return drug

        return None

    def run(self, state: TrialLensState) -> TrialLensState:

        question = state["question"]

        drug = self._extract_drug(question)

        if not drug:

            return {
                "safety_results": [],
                "errors": [
                    "Could not identify a drug for FAERS search."
                ],
                "execution_trace": [
                    "safety_agent:no_drug"
                ],
            }

        try:

            raw_data = self.faers.search_drug(
                drug_name=drug,
                limit=20,
            )

            events = self.faers.summarize_events(
                raw_data
            )

            serious_count = sum(
                1
                for event in events
                if str(event.get("serious")) == "1"
            )

            reactions = {}

            for event in events:

                for reaction in event["reactions"]:

                    reactions[reaction] = (
                        reactions.get(reaction, 0) + 1
                    )

            top_reactions = sorted(
                reactions.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:10]

            result = {
                "source": "openFDA FAERS",
                "query_type": "adverse_event_search",
                "drug": drug,
                "records_retrieved": len(events),
                "serious_events": serious_count,
                "top_reactions": [
                    {
                        "reaction": reaction,
                        "count": count,
                    }
                    for reaction, count in top_reactions
                ],
                "events": events,
            }

            return {
                "safety_results": [result],
                "execution_trace": [
                    "safety_agent"
                ],
            }

        except Exception as exc:

            return {
                "safety_results": [],
                "errors": [
                    f"FAERS API error: {exc}"
                ],
                "execution_trace": [
                    "safety_agent:error"
                ],
            }


safety_agent = SafetySignalAgent()