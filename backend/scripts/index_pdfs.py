import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.ingestion.pdf_manager import PDFIngestionManager

PDF_DIR = Path("data/sample_papers")

manager = PDFIngestionManager()

total_pdfs = 0
total_chunks = 0

for pdf in sorted(PDF_DIR.glob("*.pdf")):

    result = manager.ingest_pdf(pdf)

    if result["success"]:

        total_pdfs += 1
        total_chunks += result["chunks"]

print("\n" + "=" * 60)
print("PDF INDEXING COMPLETE")
print("=" * 60)

print(f"PDFs Indexed : {total_pdfs}")
print(f"Chunks Stored: {total_chunks}")