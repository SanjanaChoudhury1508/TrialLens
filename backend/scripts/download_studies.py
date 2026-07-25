import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.clinicaltrials_api import fetch_studies


OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

page_token = None
page = 1

MAX_PAGES = 3

while page <= MAX_PAGES:

    print(f"Downloading page {page}...")

    data = fetch_studies(
        query="lung cancer",
        page_size=100,
        page_token=page_token,
    )

    output_file = OUTPUT_DIR / f"studies_page{page}.json"

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Saved {output_file}")

    page_token = data.get("nextPageToken")

    if not page_token:
        break

    page += 1

print("Finished downloading all pages.")