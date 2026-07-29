from dataclasses import dataclass, asdict


@dataclass
class DocumentChunk:
    chunk_id: str

    document_id: str

    section: str

    text: str

    page: int | None = None

    metadata: dict | None = None

    def to_dict(self):
        return asdict(self)