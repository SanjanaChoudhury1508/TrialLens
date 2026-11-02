import math

from google import genai
from google.genai import types

from app.config import settings


class GeminiEmbeddingService:
    """
    Cloud embedding service for TrialLens.

    Uses gemini-embedding-001 with 768 dimensions.
    Local development continues using BGE embeddings.
    """

    MODEL_NAME = "gemini-embedding-001"
    DIMENSIONS = 768

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def embed(
        self,
        text: str,
        task_type: str = "RETRIEVAL_QUERY",
    ) -> list[float]:

        if not text or not text.strip():
            raise ValueError("Cannot embed empty text.")

        response = self.client.models.embed_content(
            model=self.MODEL_NAME,
            contents=text,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=self.DIMENSIONS,
            ),
        )

        embedding = response.embeddings[0].values

        if len(embedding) != self.DIMENSIONS:
            raise ValueError(
                f"Expected {self.DIMENSIONS} dimensions, "
                f"received {len(embedding)}."
            )

        # Gemini Embedding 001 requires normalization
        # when using reduced dimensions.
        magnitude = math.sqrt(
            sum(value * value for value in embedding)
        )

        if magnitude == 0:
            raise ValueError("Received zero-magnitude embedding.")

        return [
            value / magnitude
            for value in embedding
        ]
    
    def _document_config(self):
        return types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=self.DIMENSIONS,
        )