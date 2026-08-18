import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from app.database.vector_store import VectorStore
def main():

    store = VectorStore()

    query = (
        "A-BRAVE trial avelumab "
        "high-risk triple-negative breast cancer"
    )

    print("=" * 70)
    print("KEYWORD SEARCH TEST")
    print("=" * 70)

    print("\nQuery:")
    print(query)

    results = store.keyword_search(
        query,
        top_k=5,
    )

    print("\nKeyword Search Results")
    print("=" * 70)

    for i, result in enumerate(results, start=1):

        print(f"\nResult {i}")

        print(
            f"Document    : "
            f"{result['document_id']}"
        )

        print(
            f"Source Type : "
            f"{result['source_type']}"
        )

        print(
            f"Trial ID    : "
            f"{result['trial_id']}"
        )

        print(
            f"Section     : "
            f"{result['section']}"
        )

        print(
            f"Keyword Score: "
            f"{result['keyword_score']:.4f}"
        )

        print("\nContent:")

        print(
            result["content"][:1000]
        )

    print(
        f"\nResults returned: "
        f"{len(results)}"
    )


if __name__ == "__main__":
    main()