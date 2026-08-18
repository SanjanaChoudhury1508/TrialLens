import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.database.vector_store import VectorStore
from app.services.embedding_service import EmbeddingService


def main():

    query = "A-BRAVE trial primary objective avelumab high-risk triple-negative early breast cancer"

    print("=" * 70)
    print("PDF VECTOR SEARCH TEST")
    print("=" * 70)

    print(f"\nQuery:\n{query}\n")

    embedder = EmbeddingService()
    store = VectorStore()

    embedding = embedder.embed(query)

    results = store.search(
        embedding,
        top_k=5,
    )

    print("\nRetrieved PDF/Trial Chunks\n")

    for i, row in enumerate(results, start=1):

        print("=" * 70)
        print(f"Result {i}")
        print(f"Document    : {row['document_id']}")
        print(f"Source Type : {row['source_type']}")
        print(f"Trial ID    : {row['trial_id']}")
        print(f"Section     : {row['section']}")
        print(f"Distance    : {row['distance']:.4f}")
        
        print("\nContent:")
        print(row["content"][:1000])

    print("\n" + "=" * 70)
    print(f"Results returned: {len(results)}")
    print("=" * 70)


if __name__ == "__main__":
    main()