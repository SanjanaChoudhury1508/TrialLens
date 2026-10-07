from app.graph.triallens_graph import trial_lens_graph


def main():

    question = (
        "What were the median ages of patients "
        "in the avelumab and control groups?"
    )

    print("\n=== TrialLens Table LangGraph Test ===")
    print(f"Question: {question}")

    result = trial_lens_graph.invoke({
        "question": question,
    })

    print("\nIntent:")
    print(result.get("intent"))

    print("\nAgents:")
    print(result.get("agents_to_run"))

    print(
        "\nRetrieved documents:",
        len(result.get("retrieved_documents", []))
    )

    print(
        "Table results:",
        len(result.get("table_results", []))
    )

    print(
        "Evidence:",
        len(result.get("evidence", []))
    )

    print("\nDraft answer:")
    print(result.get("draft_answer"))

    print("\nVerification passed:")
    print(result.get("verification_passed"))

    print("\nVerification issues:")
    print(result.get("verification_issues"))

    print("\nFinal answer:")
    print(result.get("final_answer"))

    print("\nTrace:")
    print(
        " -> ".join(
            result.get("execution_trace", [])
        )
    )


if __name__ == "__main__":
    main()