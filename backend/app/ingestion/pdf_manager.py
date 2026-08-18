from pathlib import Path
import re
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
    Extract document metadata
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

    def extract_trial_id(self, parsed_document):
        """
        Extract an NCT Clinical Trial ID from the complete PDF document.

        This is done at document level rather than chunk level because
        the NCT ID may appear on a different page/chunk from the actual
        trial information.
        """

        try:
            text = parsed_document.export_to_text()
        except AttributeError:
            text = ""

            for item, _level in parsed_document.iterate_items():

                if hasattr(item, "text") and item.text:
                    text += item.text + "\n"

        match = re.search(
            r"\bNCT\d{8}\b",
            text,
            re.IGNORECASE,
        )

        if match:
            return match.group(0).upper()

        return None

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
        # Document metadata
        # ------------------------------------------

        document_id = pdf_path.stem

        trial_id = self.extract_trial_id(
            parsed_document
        )

        if trial_id:
            print(f"✓ Trial ID detected: {trial_id}")
        else:
            print("⚠ No NCT Trial ID detected")

        # ------------------------------------------
        # Remove previous version
        # ------------------------------------------

        self.store.delete_document(
            document_id
        )

        # ------------------------------------------
        # Chunk
        # ------------------------------------------

        chunks = self.chunker.chunk(
            parsed_document,
            document_id=document_id,
        )

        print(f"✓ {len(chunks)} chunks created")

        # ------------------------------------------
        # Store
        # ------------------------------------------

        indexed = 0

        for chunk in chunks:

            embedding = self.embedder.embed(
                chunk.text
            )

            db_chunk = DocumentChunk(
                chunk_id=str(uuid.uuid4()),
                document_id=document_id,
                section=chunk.section,
                text=chunk.text,
                page=chunk.page,
                metadata={
                    "source": "pdf",
                    "filename": pdf_path.name,
                    "trial_id": trial_id,
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
            "trial_id": trial_id,
            "chunks": indexed,
        }