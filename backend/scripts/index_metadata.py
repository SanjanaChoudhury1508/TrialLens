import json
import sys
import uuid
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.models import ClinicalTrial
from app.ingestion.text_builder import TrialTextBuilder
from app.ingestion.chunker import SemanticChunker
from app.chunk_models import DocumentChunk
from app.services.embedding_service import EmbeddingService
from app.database.vector_store import VectorStore

METADATA = Path("data/metadata/studies_metadata.json")


def load_trials():

    with METADATA.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return [ClinicalTrial(**trial) for trial in data]


def main():

    trials = load_trials()

    builder = TrialTextBuilder()
    chunker = SemanticChunker()
    embedder = EmbeddingService()
    store = VectorStore()

    total_chunks = 0

    for trial in trials:

        text = builder.build(trial)

        if not text.strip():
            continue

        chunks = chunker.chunk_text(text)

        for i, chunk_text in enumerate(chunks):

            embedding = embedder.embed(chunk_text)

            chunk = DocumentChunk(
                chunk_id=str(uuid.uuid4()),
                document_id=trial.nct_id,
                section=f"chunk_{i+1}",
                text=chunk_text,
                metadata={
                    "nct_id": trial.nct_id,
                    "brief_title": trial.brief_title,
                    "phase": trial.phase,
                    "status": trial.status,
                    "study_type": trial.study_type,
                    "source": "clinicaltrials",
                },
            )

            store.insert_chunk(chunk, embedding)

            total_chunks += 1

    print("=" * 50)
    print(f"Trials indexed : {len(trials)}")
    print(f"Chunks created : {total_chunks}")
    print("=" * 50)


if __name__ == "__main__":
    main()