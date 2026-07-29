import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.pubmed_api import (
    search_by_nct_id,
    fetch_article_details,
    parse_articles,
)

METADATA = Path("data/metadata/studies_metadata.json")
OUTPUT = Path("data/metadata/document_index.json")

with METADATA.open("r", encoding="utf-8") as f:
    studies = json.load(f)

documents = []

for study in studies:

    nct = study["nct_id"]

    print(f"Searching {nct}")

    search = search_by_nct_id(nct)

    ids = search["esearchresult"]["idlist"]

    if not ids:
        continue

    details = fetch_article_details(ids)

    documents.extend(parse_articles(nct, details))

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(
        [doc.to_dict() for doc in documents],
        f,
        indent=2,
    )

print(f"\nDiscovered {len(documents)} documents.")
print(f"Saved to {OUTPUT}")