from app.agents.state import TrialLensState


def route_question(state: TrialLensState) -> TrialLensState:
    """
    Determine which specialist agents are relevant to the question.

    Routing is deterministic and does not consume an LLM call.
    """

    question = state.get("question", "").lower()

    agents = ["retriever"]

    # ---------------------------------------------------------
    # Safety-related questions
    # ---------------------------------------------------------

    safety_terms = [
        "adverse event",
        "adverse events",
        "safety",
        "toxicity",
        "side effect",
        "side effects",
        "faers",
        "signal",
    ]

    # ---------------------------------------------------------
    # ClinicalTrials.gov structured questions
    # ---------------------------------------------------------

    structured_terms = [
        "recruiting",
        "recruitment",
        "eligibility",
        "location",
        "status",
        "phase",
        "how many trials",
    ]

    # ---------------------------------------------------------
    # Table-related questions
    # ---------------------------------------------------------

    table_terms = [
        "table",
        "baseline characteristics",
        "baseline characteristic",
        "median age",
        "age",
        "ecog",
        "her2",
        "brca",
        "er expression",
        "treatment group",
        "control group",
        "avelumab group",
        "patient characteristics",
        "patient characteristic",
        "n (%)",
        "percentage",
    ]

    if any(term in question for term in safety_terms):
        agents.append("safety")

    if any(term in question for term in structured_terms):
        agents.append("structured")

    if any(term in question for term in table_terms):
        agents.append("table")

    return {
        "intent": (
            "multi_agent"
            if len(agents) > 1
            else "retrieval"
        ),
        "agents_to_run": list(dict.fromkeys(agents)),
        "execution_trace": ["router"],
    }