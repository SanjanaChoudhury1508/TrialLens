import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.retrieval_service import RetrievalService


def main():

    retriever = RetrievalService()

    queries = [
        "What type of cancer is investigated in the phase III breast immunotherapy trial?",
        "high-risk early triple-negative breast cancer",
        "A-BRAVE triple-negative breast cancer",
    ]

    for query in queries:

        print("\n")
        print("=" * 70)
        print("QUERY")
        print("=" * 70)
        print(query)

        results = retriever.retrieve(
            query,
            top_k=5,
        )

        print("\nRESULTS")
        print("=" * 70)

        for rank, result in enumerate(
            results,
            start=1,
        ):

            print(
                f"\nRank {rank}"
            )

            print(
                f"Document: "
                f"{result.get('document_id')}"
            )

            print(
                f"Trial ID: "
                f"{result.get('trial_id')}"
            )

            print(
                f"RRF Score: "
                f"{result.get('rrf_score')}"
            )

            print(
                f"Rerank Score: "
                f"{result.get('rerank_score')}"
            )

            print(
                f"Content:\n"
                f"{result.get('content', '')[:500]}"
            )


if __name__ == "__main__":
    main()