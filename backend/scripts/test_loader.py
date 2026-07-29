import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.ingestion.loader import DocumentLoader

loader = DocumentLoader(
    Path("data/metadata/document_index.json")
)

documents = loader.load()

print(f"Loaded {len(documents)} documents\n")

for doc in documents[:5]:
    print(doc)