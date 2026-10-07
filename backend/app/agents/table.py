from app.agents.state import TrialLensState
from app.retrieval.table_retriever import TableRetriever
from app.agents.table_qa_agent import TableQAAgent


class TableAgent:

    def __init__(self):
        self.retriever = TableRetriever()
        self.qa = TableQAAgent()

    def run(
        self,
        state: TrialLensState,
    ) -> TrialLensState:

        question = state["question"]

        try:

            # -------------------------------------------------
            # First attempt: use the complete question
            # -------------------------------------------------

            tables = self.retriever.retrieve(
                query=question,
                top_k=5,
            )

            # -------------------------------------------------
            # Fallback for common table questions
            # -------------------------------------------------

            if not tables:

                question_lower = question.lower()

                search_terms = []

                if "median age" in question_lower:
                    search_terms.extend([
                        "age",
                        "median",
                    ])

                if "baseline" in question_lower:
                    search_terms.extend([
                        "baseline",
                        "characteristics",
                    ])

                if "ecog" in question_lower:
                    search_terms.append("ECOG")

                if "her2" in question_lower:
                    search_terms.append("HER2")

                if "brca" in question_lower:
                    search_terms.append("BRCA")

                if "avelumab" in question_lower:
                    search_terms.append("avelumab")

                if "control" in question_lower:
                    search_terms.append("control")

                if search_terms:

                    tables = self.retriever.retrieve(
                        query=" ".join(
                            dict.fromkeys(search_terms)
                        ),
                        top_k=5,
                    )

            # -------------------------------------------------
            # No table found
            # -------------------------------------------------

            if not tables:

                return {
                    "table_results": [],
                    "execution_trace": [
                        "table_agent:no_results"
                    ],
                }

            # -------------------------------------------------
            # Table QA
            # -------------------------------------------------

            result = self.qa.answer(
                question=question,
                tables=tables,
            )

            # -------------------------------------------------
            # Store structured table evidence
            # -------------------------------------------------

            table_results = []

            for table in tables:

                table_results.append({
                    "source_type": "Clinical PDF Table",
                    "table_id": table["table_id"],
                    "document_id": table["document_id"],
                    "trial_id": table["trial_id"],
                    "title": table["title"],
                    "page": table["page"],
                    "headers": table["headers"],
                    "rows": table["rows"],
                    "answer": result.get(
                        "answer",
                        "",
                    ),
                })

            return {
                "table_results": table_results,
                "execution_trace": [
                    "table_agent"
                ],
            }

        except Exception as exc:

            return {
                "table_results": [],
                "errors": [
                    f"Table agent error: {exc}"
                ],
                "execution_trace": [
                    "table_agent:error"
                ],
            }


table_agent = TableAgent()