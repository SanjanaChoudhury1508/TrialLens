import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.database.vector_store import VectorStore
from app.services.embedding_service import EmbeddingService

embedder = EmbeddingService()
store = VectorStore()

query = "phase III immunotherapy"

embedding = embedder.embed(query)

results = store.search(embedding, top_k=5)

print("\nSearch Results\n")

for i, row in enumerate(results, start=1):
    print("=" * 60)
    print(f"Result {i}")
    print(f"Document: {row['document_id']}")
    print(f"Section : {row['section']}")
    print(f"Distance: {row['distance']:.4f}")
    print(row["content"][:300])