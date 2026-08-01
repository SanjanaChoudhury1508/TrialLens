import uuid

from app.chunk_models import DocumentChunk
from app.document_structure import ParsedDocument


class SemanticChunker:

    def chunk(
        self,
        document: ParsedDocument,
    ) -> list[DocumentChunk]:

        chunks = []

        for section in document.sections:

            text = section.text.strip()

            if not text:
                continue

            chunks.append(
                DocumentChunk(
                    chunk_id=str(uuid.uuid4()),
                    document_id=document.document_id,
                    section=section.title,
                    text=text,
                    page=section.page,
                    metadata={
                        "level": section.level
                    }
                )
            )

        return chunks
    def chunk_text(self, text, chunk_size=600, overlap=100):

        chunks = []

        start = 0

        while start < len(text):

            end = min(start + chunk_size, len(text))

            chunks.append(text[start:end])

            start += chunk_size - overlap

        return chunks