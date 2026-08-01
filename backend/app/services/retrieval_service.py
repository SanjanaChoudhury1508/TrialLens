from app.database.vector_store import VectorStore
from app.services.embedding_service import EmbeddingService


class RetrievalService:
    """
    Retrieves the most relevant chunks from the vector database.
    """

    def __init__(self):

        self.embedder = EmbeddingService()
        self.store = VectorStore()

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
    ):

        # Convert question into embedding
        embedding = self.embedder.embed(question)

        # Search pgvector
        results = self.store.search(
            embedding,
            top_k=top_k,
        )

        return results