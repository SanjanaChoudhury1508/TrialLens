import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.embedding_service import EmbeddingService

service = EmbeddingService()

vector = service.embed(
    "Patients received chemotherapy every three weeks."
)

print(f"Embedding dimension: {len(vector)}")
print(vector[:10])