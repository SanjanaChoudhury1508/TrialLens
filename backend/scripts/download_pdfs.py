import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.pdf_downloader import download_pmc_pdf

INDEX = Path("data/metadata/document_index.json")
PDF_DIR = Path("data/pdfs")

PDF_DIR.mkdir(parents=True, exist_ok=True)

with INDEX.open("r", encoding="utf-8") as f:
    documents = json.load(f)

downloaded = 0
already_exists = 0
skipped = 0
failed = 0

for doc in documents:

    pmcid = doc.get("pmcid")

    if not pmcid:
        skipped += 1
        continue

    existing_path = doc.get("local_path")

    if existing_path and Path(existing_path).exists():
        already_exists += 1
        continue

    print(f"\nDownloading {pmcid}...")

    try:
        result = download_pmc_pdf(pmcid, PDF_DIR)

        if result:
            downloaded += 1

            doc["local_path"] = str(result)

            print(f"✓ Saved: {result.name}")

        else:
            failed += 1
            print("✗ PDF not available")

    except Exception as e:
        failed += 1
        print(f"✗ Error: {e}")

with INDEX.open("w", encoding="utf-8") as f:
    json.dump(documents, f, indent=2)

print("\n" + "=" * 50)
print("PDF Download Summary")
print("=" * 50)
print(f"Total documents : {len(documents)}")
print(f"Downloaded      : {downloaded}")
print(f"Already present : {already_exists}")
print(f"Skipped         : {skipped}")
print(f"Failed          : {failed}")