from pathlib import Path

from app.ingestion.loader import DocumentLoader
from app.ingestion.parser import TrialDocumentParser
from app.ingestion.chunker import SemanticChunker
from app.services.embedding_service import EmbeddingService
from app.database.vector_store import VectorStore


def main():
    print("=" * 60)
    print("TrialLens Document Indexing Pipeline")
    print("=" * 60)

    loader = DocumentLoader()
    parser = TrialDocumentParser()
    chunker = SemanticChunker()
    embedder = EmbeddingService()
    store = VectorStore()

    documents = loader.load()

    print(f"\nLoaded {len(documents)} discovered documents.\n")

    processed_docs = 0
    skipped_docs = 0
    total_chunks = 0

    for doc in documents:

        if not doc.local_path:
            skipped_docs += 1
            continue

        pdf_path = Path(doc.local_path)

        if not pdf_path.exists():
            skipped_docs += 1
            continue

        print(f"\nProcessing: {pdf_path.name}")

        try:
            parsed_document = parser.parse(pdf_path)

            chunks = chunker.chunk(parsed_document)

            print(f"Generated {len(chunks)} chunks")

            for chunk in chunks:

                embedding = embedder.embed(chunk.text)

                store.insert_chunk(
                    chunk,
                    embedding
                )

                total_chunks += 1

            processed_docs += 1

            print(f"Indexed {pdf_path.name}")

        except Exception as e:
            print(f"Failed: {pdf_path.name}")
            print(e)

    print("\n" + "=" * 60)
    print("Indexing Complete")
    print("=" * 60)
    print(f"Documents processed : {processed_docs}")
    print(f"Documents skipped   : {skipped_docs}")
    print(f"Chunks stored       : {total_chunks}")


if __name__ == "__main__":
    main()