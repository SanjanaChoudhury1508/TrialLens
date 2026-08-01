class PromptBuilder:
    """
    Builds the prompt sent to the LLM.
    """

    @staticmethod
    def build(question: str, chunks):

        evidence = []

        for i, chunk in enumerate(chunks, start=1):

            evidence.append(
                f"""
========== Evidence {i} ==========
Clinical Trial ID:
{chunk['document_id']}

Section:
{chunk['section']}

Content:
{chunk['content']}
"""
            )

        prompt = f"""
You are TrialLens, an AI assistant specialized in clinical trials.

Use ONLY the evidence provided below.

Rules:

1. Do not make up facts.
2. If the evidence is insufficient, say so.
3. Cite the Clinical Trial IDs (NCT IDs) whenever appropriate.
4. Answer in clear medical language.

User Question:

{question}

Evidence:

{''.join(evidence)}

Answer:
"""

        return prompt.strip()