from app.chunk_models import DocumentChunk
import uuid


class SemanticChunker:
    """
    Chunk a DoclingDocument by splitting its exported markdown.
    """

    def chunk(self, document):

        # Export the parsed document as Markdown
        markdown = document.export_to_markdown()

        return self.chunk_markdown(markdown)

    def chunk_markdown(
        self,
        markdown: str,
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> list[DocumentChunk]:

        chunks = []

        start = 0
        chunk_number = 1

        while start < len(markdown):

            end = min(start + chunk_size, len(markdown))

            text = markdown[start:end].strip()

            if text:

                chunks.append(

                    DocumentChunk(

                        chunk_id=str(uuid.uuid4()),

                        document_id="",

                        section=f"chunk_{chunk_number}",

                        text=text,

                        page=1,

                        metadata={},
                    )

                )

                chunk_number += 1

            start += chunk_size - overlap

        return chunks