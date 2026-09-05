from app.agents.structured_agent import structured_agent


def main():

    state = {
        "question": "What is the current status of NCT02926196?"
    }

    result = structured_agent.run(state)

    print("\n=== Structured Data Agent Test ===")

    print("Results:")
    print(result.get("structured_results"))

    print("\nErrors:")
    print(result.get("errors", []))

    print("\nTrace:")
    print(result.get("execution_trace"))


if __name__ == "__main__":
    main()