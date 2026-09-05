class PromptBuilder:
    """
    Builds the grounded prompt sent to the LLM.
    """

    @staticmethod
    def build(
        question: str,
        chunks,
        conversation_context: str | None = None,
    ):

        evidence = []

        for i, chunk in enumerate(chunks, start=1):

            source_type = chunk.get(
                "source_type",
                chunk.get("source", "Unknown"),
            )
                        # -------------------------------------------------
            # SAFETY / FAERS EVIDENCE
            # -------------------------------------------------

            if chunk.get("source_type") == "safety":

                drug = chunk.get(
                    "drug",
                    "Not identified",
                )

                records = chunk.get(
                    "records_retrieved",
                    0,
                )

                serious_events = chunk.get(
                    "serious_events",
                    0,
                )

                top_reactions = chunk.get(
                    "top_reactions",
                    [],
                )

                evidence.append(
                    f"""
========== Evidence {i} ==========

Source:
openFDA FAERS

Source Type:
Pharmacovigilance / Adverse Event Data

Drug:
{drug}

FAERS Records Retrieved:
{records}

Records Marked Serious:
{serious_events}

Top Reported Reactions:
{top_reactions}

Important interpretation:
These are adverse-event reports retrieved from FAERS.
They do not establish that the drug caused the reported event.
"""
                )

                continue
            # -------------------------------------------------
            # STRUCTURED DATA EVIDENCE
            # -------------------------------------------------

            if "data" in chunk:

                data = chunk.get("data", {})

                nct_id = data.get(
                    "nct_id",
                    "Not identified",
                )

                evidence.append(
                    f"""
========== Evidence {i} ==========

Source:
ClinicalTrials.gov

Source Type:
Structured Clinical Trial Data

Clinical Trial ID:
{nct_id}

Trial Title:
{data.get("title", "Not available")}

Official Title:
{data.get("official_title", "Not available")}

Overall Status:
{data.get("overall_status", "Not available")}

Phase:
{", ".join(data.get("phase", []))}

Study Type:
{data.get("study_type", "Not available")}

Start Date:
{data.get("start_date", "Not available")}

Completion Date:
{data.get("completion_date", "Not available")}

Enrollment:
{data.get("enrollment", "Not available")}

Enrollment Type:
{data.get("enrollment_type", "Not available")}

Sponsor:
{data.get("sponsor", "Not available")}

Locations:
{data.get("locations", "Not available")}

Summary:
{data.get("brief_summary", "Not available")}
"""
                )

                continue

            # -------------------------------------------------
            # DOCUMENT / RAG EVIDENCE
            # -------------------------------------------------

            document_id = chunk.get(
                "document_id",
                "Unknown",
            )

            trial_id = chunk.get("trial_id")

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

        # -------------------------------------------------
        # CONVERSATION CONTEXT
        # -------------------------------------------------

        context_section = ""

        if conversation_context:
            context_section = f"""
PREVIOUS CONVERSATION CONTEXT:

{conversation_context}

Use the previous conversation ONLY to resolve references
in the user's current question, such as:
- "the trial"
- "this trial"
- "that treatment"
- "what about overall survival?"
- "what about the patients?"

The previous conversation is NOT evidence.

Do NOT treat facts from previous answers as evidence.
Every factual claim in the final answer must be independently
supported by the retrieved evidence below.

The previous conversation may help identify which clinical trial
the user is referring to, but it must never be used to invent,
add, or assume facts that are not present in the retrieved evidence.
"""

        # -------------------------------------------------
        # GROUNDED PROMPT
        # -------------------------------------------------

        prompt = f"""
You are TrialLens, an AI assistant specialized in clinical trial research.

Your task is to answer the user's question using ONLY the evidence provided below.

IMPORTANT GROUNDING RULES:

1. Use ONLY information explicitly supported by the provided evidence.
   Do not use outside knowledge.

2. Do not invent, infer, or assume facts that are not supported by the evidence.

3. If the evidence is insufficient to answer the question, say:
   "The available evidence is insufficient to answer this question."

4. Clinical trial identity is extremely important.
   A Clinical Trial ID (NCT ID) identifies a specific trial.

5. NEVER combine facts from different clinical trials unless the user
   explicitly asks for a comparison between trials.

6. If the evidence contains multiple Clinical Trial IDs and the user's
   question clearly refers to one trial, use ONLY evidence belonging
   to that trial.

7. If the question does not identify a specific trial and the evidence
   contains multiple different trials, do NOT combine their findings.

   If conversation context clearly identifies the intended trial,
   use that context only to resolve the trial identity.

   If there is still not enough context to determine which trial
   the user means, say:
   "Please specify which clinical trial you are referring to."

8. When a Clinical Trial ID is available, include the NCT ID when
   identifying the trial.

9. Prefer the NCT ID over the document filename when identifying a trial.

10. Multiple evidence chunks with the same Clinical Trial ID should
    be treated as supporting evidence from the same trial.

11. Do not use a fact from one trial to answer a question about another trial.

12. Do not mention unrelated trials merely because they contain similar
    terminology, outcomes, treatments, or statistics.

13. Do not expose internal retrieval metadata such as:
    - document filenames
    - relevance scores
    - reranker scores
    - evidence numbers
    - "Source:" labels
    - internal database identifiers

14. Write the final answer naturally for a clinical research user.
    Do not describe the retrieval process.

15. Answer clearly and concisely using appropriate clinical terminology.

16. If the evidence contains the exact numerical result requested,
    report that result accurately, including its confidence interval or
    statistical significance when explicitly provided.

17. Do not provide medical advice or treatment recommendations.

CONTEXT RULE:

The current question may be a follow-up to an earlier question about
a specific clinical trial.

If the question itself does not name a trial, conversation context may
be used to determine which trial the user is referring to.

However, conversation context is ONLY for resolving the user's intent.
It is NOT a source of factual evidence.

All factual statements in the final answer must be supported by the
retrieved evidence.

If multiple trials remain possible after considering the question,
conversation context, and retrieved evidence, do not guess. Ask the
user to specify the clinical trial.

{context_section}

USER QUESTION:

{question}

EVIDENCE:

{''.join(evidence)}

FINAL ANSWER:
"""

        return prompt.strip()