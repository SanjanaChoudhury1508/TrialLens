import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)
from app.services.retrieval_service import RetrievalService
from app.services.reranker import Reranker


def main():

    print("=" * 70)
    print("RERANKER TEST")
    print("=" * 70)

    question = (
        "A-BRAVE trial primary objective "
        "avelumab high-risk triple-negative early breast cancer"
    )

    print("\nQuery:")
    print(question)

    # ------------------------------------------
    # Retrieve candidates
    # ------------------------------------------

    retriever = RetrievalService()

    print("\nRetrieving candidates...")

    results = retriever.retrieve(
        question,
        top_k=20,
    )

    print(f"Retrieved {len(results)} candidates")

    # ------------------------------------------
    # Rerank
    # ------------------------------------------

    reranker = Reranker()

    print("\nReranking candidates...")

    reranked = reranker.rerank(
        question,
        results,
        top_k=5,
    )

    # ------------------------------------------
    # Display
    # ------------------------------------------

    print("\n")
    print("=" * 70)
    print("RERANKED RESULTS")
    print("=" * 70)

    for i, result in enumerate(
        reranked,
        start=1,
    ):

        print(f"\nResult {i}")

        print(
            f"Document    : "
            f"{result.get('document_id')}"
        )

        print(
            f"Trial ID    : "
            f"{result.get('trial_id')}"
        )

        print(
            f"Source Type : "
            f"{result.get('source_type')}"
        )

        print(
            f"Section     : "
            f"{result.get('section')}"
        )

        print(
            f"Vector/Hybrid Score : "
            f"{result.get('score', result.get('distance', 'N/A'))}"
        )

        print(
            f"Rerank Score: "
            f"{result.get('rerank_score'):.4f}"
        )

        print("\nContent:")

        content = result.get(
            "content",
            "",
        )

        print(content[:1000])

        print("-" * 70)


if __name__ == "__main__":
    main()