import sys
import uuid
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.chunk_models import DocumentChunk
from app.database.vector_store import VectorStore
from app.services.embedding_service import EmbeddingService

chunk = DocumentChunk(
    chunk_id=str(uuid.uuid4()),
    document_id="TEST001",
    section="Methods",
    text="Patients received chemotherapy every three weeks.",
    page=1,
    metadata={"source": "unit-test"},
)

embedding_service = EmbeddingService()
embedding = embedding_service.embed(chunk.text)

store = VectorStore()
store.insert_chunk(chunk, embedding)

print("Chunk stored successfully!")