import sys
from pathlib import Path

# Add backend directory to Python path
BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from app.services.retrieval_service import RetrievalService


def main():

    print("=" * 70)
    print("HYBRID RETRIEVAL TEST")
    print("=" * 70)

    question = (
        "A-BRAVE trial primary objective "
        "avelumab high-risk triple-negative "
        "early breast cancer"
    )

    print("\nQuery:")
    print(question)

    retriever = RetrievalService()

    results = retriever.retrieve(
        question,
        top_k=5,
    )

    print("\nHybrid Retrieval Results")
    print("=" * 70)

    for i, result in enumerate(results, start=1):

        print(f"\nResult {i}")

        print(
            f"Document    : "
            f"{result.get('document_id')}"
        )

        print(
            f"Source Type : "
            f"{result.get('source_type')}"
        )

        print(
            f"Trial ID    : "
            f"{result.get('trial_id')}"
        )

        print(
            f"Section     : "
            f"{result.get('section')}"
        )

        print(
            f"RRF Score   : "
            f"{result.get('rrf_score', 0):.6f}"
        )

        print(
            f"\nContent:\n"
            f"{result.get('content')}"
        )

    print("\n" + "=" * 70)

    print(
        f"Results returned: {len(results)}"
    )


if __name__ == "__main__":
    main()