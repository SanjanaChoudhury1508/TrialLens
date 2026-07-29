from dataclasses import dataclass


@dataclass
class EmbeddedChunk:
    chunk_id: str

    embedding: list[float]

    metadata: dict