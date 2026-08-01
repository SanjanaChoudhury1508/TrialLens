import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.retrieval_service import RetrievalService

retriever = RetrievalService()

question = "breast cancer immunotherapy"

results = retriever.retrieve(question)

print("\nRetrieved Chunks\n")

for i, chunk in enumerate(results, start=1):

    print("=" * 70)
    print(f"Result {i}")
    print(f"Document : {chunk['document_id']}")
    print(f"Section  : {chunk['section']}")
    print(f"Distance : {chunk['distance']:.4f}")
    print()
    print(chunk["content"][:500])