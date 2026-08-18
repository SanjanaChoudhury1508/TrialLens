class PromptBuilder:
    """
    Builds the grounded prompt sent to the LLM.
    """

    @staticmethod
    def build(question: str, chunks):

        evidence = []

        for i, chunk in enumerate(
            chunks,
            start=1,
        ):

            document_id = chunk.get(
                "document_id",
                "Unknown",
            )

            source_type = chunk.get(
                "source_type",
                "Unknown",
            )

            trial_id = chunk.get(
                "trial_id"
            )

            section = chunk.get(
                "section",
                "Unknown",
            )

            content = chunk.get(
                "content",
                "",
            )

            trial_reference = (
                trial_id
                if trial_id
                else "Not identified"
            )

            evidence.append(
                f"""
========== Evidence {i} ==========

Document:
{document_id}

Source Type:
{source_type}

Clinical Trial ID:
{trial_reference}

Section:
{section}

Content:
{content}
"""
            )

        prompt = f"""
You are TrialLens, an AI assistant specialized
in clinical trials.

Your task is to answer the user's question using
ONLY the evidence provided below.

IMPORTANT RULES:

1. Do not use outside knowledge.

2. Do not invent or infer facts that are not
   supported by the evidence.

3. If the evidence is insufficient, explicitly
   say that the available evidence is insufficient.

4. When a Clinical Trial ID (NCT ID) is provided
   in the evidence, cite it in the answer.

5. Prefer the NCT ID over the document filename
   when identifying a clinical trial.

6. If multiple evidence chunks belong to the same
   trial, treat them as supporting evidence from
   the same source rather than separate trials.

7. Distinguish between:
   - ClinicalTrials.gov metadata
   - Clinical PDF documents
   - Other documents

8. Do not claim that a trial is currently recruiting
   unless the evidence explicitly states its
   recruitment status.

9. Answer clearly and concisely using appropriate
   clinical terminology.

10. Do not provide medical advice or treatment
    recommendations.

User Question:

{question}

Evidence:

{''.join(evidence)}

Answer:
"""

        return prompt.strip()