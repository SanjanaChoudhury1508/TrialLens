from typing import Any

from app.services.llm_service import LLMService


class TableQAAgent:

    def __init__(self):
        self.llm = LLMService()

    def answer(
        self,
        question: str,
        tables: list[dict[str, Any]],
    ) -> dict[str, Any]:

        if not tables:
            return {
                "answer": "No relevant clinical trial table was found.",
                "sources": [],
                "success": False,
            }

        table_context = self._build_table_context(tables)

        prompt = self._build_prompt(
            question=question,
            table_context=table_context,
        )

        try:
            answer = self.llm.generate(prompt)

            return {
                "answer": answer,
                "sources": [
                    {
                        "type": "Clinical PDF Table",
                        "table_id": table["table_id"],
                        "document_id": table["document_id"],
                        "trial_id": table["trial_id"],
                        "title": table["title"],
                        "page": table["page"],
                    }
                    for table in tables
                ],
                "success": True,
            }

        except Exception as exc:

            return {
                "answer": "",
                "sources": [],
                "success": False,
                "error": f"Table QA error: {exc}",
            }

    # =========================================================
    # TABLE CONTEXT
    # =========================================================

    def _build_table_context(
        self,
        tables: list[dict[str, Any]],
    ) -> str:

        contexts = []

        for table in tables:

            headers = table.get("headers", [])
            rows = table.get("rows", [])

            lines = [
                f"Table title: {table.get('title')}",
                f"Trial ID: {table.get('trial_id')}",
                f"Page: {table.get('page')}",
                "",
                "Columns:",
                " | ".join(str(header) for header in headers),
                "",
                "Rows:",
            ]

            for row in rows:

                lines.append(
                    " | ".join(
                        str(value)
                        for value in row
                    )
                )

            contexts.append(
                "\n".join(lines)
            )

        return "\n\n".join(contexts)

    # =========================================================
    # PROMPT
    # =========================================================

    def _build_prompt(
        self,
        question: str,
        table_context: str,
    ) -> str:

        return f"""
You are the Table QA agent for TrialLens,
an evidence-grounded clinical trial intelligence system.

Answer the user's question using ONLY the structured
clinical-trial table provided below.

Do not use outside knowledge.

Do not invent, estimate, infer, or calculate values
unless the calculation is directly required and can
be performed from the provided table.

Preserve numerical values exactly as they appear.

If the table does not contain enough information to
answer the question, say:

"Insufficient evidence in the retrieved table."

When answering:

- Be concise and direct.
- Clearly identify the relevant treatment/group columns.
- Preserve units and percentages.
- Do not confuse randomized population counts with
  other analysis populations.
- If ranges are present, include them when relevant.
- Do not mention information that is not supported
  by the table.

USER QUESTION:
{question}

RETRIEVED TABLE:
{table_context}

ANSWER:
""".strip()