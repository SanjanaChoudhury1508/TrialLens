from app.agents.state import TrialLensState


def aggregate_evidence(state: TrialLensState) -> TrialLensState:

    evidence = []

    # RAG / PDF evidence
    for document in state.get("retrieved_documents", []):
        evidence.append({
            "source_type": "document",
            **document,
        })

    # ClinicalTrials.gov structured evidence
    for result in state.get("structured_results", []):
        evidence.append({
            "source_type": "structured",
            **result,
        })

    # FAERS / safety evidence
    for result in state.get("safety_results", []):
        evidence.append({
            "source_type": "safety",
            **result,
        })

    return {
        "evidence": evidence,
        "execution_trace": ["evidence_aggregator"],
    }