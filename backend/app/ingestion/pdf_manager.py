from pathlib import Path
import uuid

from app.ingestion.parser import TrialDocumentParser
from app.ingestion.chunker import SemanticChunker
from app.services.embedding_service import EmbeddingService
from app.database.vector_store import VectorStore
from app.chunk_models import DocumentChunk


class PDFIngestionManager:
    """
    End-to-end PDF ingestion pipeline.

    PDF
      ↓
    Parse
      ↓
    Chunk
      ↓
    Embed
      ↓
    Store
    """

    def __init__(self):

        self.parser = TrialDocumentParser()
        self.chunker = SemanticChunker()
        self.embedder = EmbeddingService()
        self.store = VectorStore()

    def ingest_pdf(
        self,
        pdf_path: Path,
    ):

        print("=" * 70)
        print(f"Indexing {pdf_path.name}")
        print("=" * 70)

        if not pdf_path.exists():

            print("PDF does not exist.")

            return {
                "success": False,
                "reason": "PDF not found",
            }

        # ------------------------------------------
        # Parse
        # ------------------------------------------

        parsed_document = self.parser.parse(pdf_path)

        print("✓ Parsed")

        # ------------------------------------------
        # Chunk
        # ------------------------------------------

        chunks = self.chunker.chunk(parsed_document)

        print(f"✓ {len(chunks)} chunks created")

        # ------------------------------------------
        # Document ID
        # ------------------------------------------

        document_id = pdf_path.stem

        indexed = 0

        # ------------------------------------------
        # Store
        # ------------------------------------------

        for i, chunk in enumerate(chunks, start=1):

            embedding = self.embedder.embed(chunk.text)

            db_chunk = DocumentChunk(
            chunk_id=str(uuid.uuid4()),
            document_id=document_id,
            section=chunk.section,
            text=chunk.text,
            page=chunk.page,
            metadata={
                "source": "pdf",
                "filename": pdf_path.name,
                **chunk.metadata,
            },
        )

            self.store.insert_chunk(
                db_chunk,
                embedding,
            )

            indexed += 1

        print(f"✓ Indexed {indexed} chunks")

        return {

            "success": True,

            "document": document_id,

            "chunks": indexed,
        }