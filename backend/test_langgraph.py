from app.graph.triallens_graph import trial_lens_graph


def main():

    result = trial_lens_graph.invoke(
        {
            "question": (
                "What safety signals and adverse events have been "
                "reported for avelumab, and what is the current status "
                "of NCT02926196?"
            )
        }
    )
    print("\n=== TrialLens LangGraph Test ===")

    print("Question:", result["question"])
    print("Intent:", result.get("intent"))
    print("Agents:", result.get("agents_to_run"))

    print(
        "Retrieved documents:",
        len(result.get("retrieved_documents", []))
    )

    print(
        "Structured results:",
        len(result.get("structured_results", []))
    )

    print(
        "Safety results:",
        len(result.get("safety_results", []))
    )

    print(
        "Evidence:",
        len(result.get("evidence", []))
    )

    print("\nDraft answer:")
    print(result.get("draft_answer", ""))

    print("\nVerification passed:")
    print(result.get("verification_passed"))

    print("\nVerification issues:")
    for issue in result.get("verification_issues", []):
        print("-", issue)

    print("\nFinal answer:")
    print(result.get("final_answer", ""))

    print("\nTrace:")
    print(" -> ".join(result.get("execution_trace", [])))


if __name__ == "__main__":
    main()