from app.retrieval.table_retriever import TableRetriever
from app.agents.table_qa_agent import TableQAAgent


def main():

    question = (
        "What were the median ages of patients "
        "in the avelumab and control groups?"
    )

    retriever = TableRetriever()

    tables = retriever.retrieve(
        query="age median",
        top_k=5,
        trial_id="NCT02926196",
    )

    print("\n" + "=" * 70)
    print("TABLE QA TEST")
    print("=" * 70)

    print(f"Retrieved tables: {len(tables)}")

    agent = TableQAAgent()

    result = agent.answer(
        question=question,
        tables=tables,
    )

    print("\nANSWER")
    print("-" * 70)
    print(result["answer"])

    print("\nSOURCES")
    print("-" * 70)

    for source in result["sources"]:
        print(source)


if __name__ == "__main__":
    main()