import json
import sys

from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.pdf_downloader import download_pmc_pdf
INDEX = Path("data/metadata/document_index.json")
PDF_DIR = Path("data/pdfs")

with INDEX.open("r", encoding="utf-8") as f:
    documents = json.load(f)

downloaded = 0

for doc in documents:

    pmcid = doc.get("pmcid")

    if not pmcid:
        continue

    print(f"Downloading {pmcid}")

    result = download_pmc_pdf(pmcid, PDF_DIR)

    if result:
        downloaded += 1
        print("✓", result.name)
    else:
        print("✗ Not available")

print(f"\nDownloaded {downloaded} PDFs")