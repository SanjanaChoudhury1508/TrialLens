import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.document_structure import (
    ParsedDocument,
    DocumentSection,
)

from app.ingestion.chunker import SemanticChunker

doc = ParsedDocument(
    document_id="TEST001",
    title="Dummy Study",
)

doc.sections.append(
    DocumentSection(
        title="Methods",
        level=1,
        text="This is the methods section.",
        page=2,
    )
)

doc.sections.append(
    DocumentSection(
        title="Results",
        level=1,
        text="These are the study results.",
        page=5,
    )
)

chunker = SemanticChunker()

chunks = chunker.chunk(doc)

for chunk in chunks:
    print(chunk)