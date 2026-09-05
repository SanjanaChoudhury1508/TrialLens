from app.agents.safety_agent import safety_agent


def main():

    state = {
        "question": "What adverse events are reported for avelumab?"
    }

    result = safety_agent.run(state)

    print("\n=== Safety Signal Agent Test ===")

    print("\nResults:")
    print(result.get("safety_results"))

    print("\nErrors:")
    print(result.get("errors", []))

    print("\nTrace:")
    print(result.get("execution_trace"))


if __name__ == "__main__":
    main()