import re
from app.agents.state import TrialLensState


def verify_answer(state: TrialLensState) -> TrialLensState:
    answer = state.get("draft_answer", "")
    evidence = state.get("evidence", [])

    if not answer:
        return {
            "final_answer": "",
            "verification_passed": False,
            "verification_issues": ["No draft answer was generated."],
            "execution_trace": ["critic_verifier"],
        }

    evidence_text = "\n".join(
        str(item.get("content", item))
        for item in evidence
    ).lower()

    issues = []

    # Verify important numeric claims appearing in the answer.
    numbers = re.findall(r"\b\d+(?:\.\d+)?%?\b", answer)

    for number in numbers:
        normalized = number.lower()

        # Ignore very common non-evidence numbers.
        if normalized in {"1", "2", "3", "4", "5"}:
            continue

        if normalized not in evidence_text:
            issues.append(
                f"Numeric claim '{number}' was not found in retrieved evidence."
            )

        # -------------------------------------------------
    # FAERS CAUSALITY CHECK
    # -------------------------------------------------

    has_faers = any(
        item.get("source_type") == "safety"
        for item in evidence
    )

    causal_terms = [
        "caused by",
        "causes",
        "caused",
        "proves that",
        "confirmed to cause",
        "due to avelumab",
        "due to the drug",
    ]

    if has_faers:

        answer_lower = answer.lower()

        for term in causal_terms:

            if term in answer_lower:

                issues.append(
                    "Answer may incorrectly imply causality "
                    "from FAERS reports. FAERS reports describe "
                    "reported adverse events and do not establish "
                    "drug-event causality."
                )

                break
    passed = len(issues) == 0

    return {
        "final_answer": answer if passed else answer,
        "verification_passed": passed,
        "verification_issues": issues,
        "execution_trace": ["critic_verifier"],
    }