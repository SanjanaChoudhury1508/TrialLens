import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.ingestion.pdf_manager import PDFIngestionManager

manager = PDFIngestionManager()

result = manager.ingest(
    pmcid="PMC9641040",
    output_dir=Path("data/pdfs"),
)

print()
print(result)