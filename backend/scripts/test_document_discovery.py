import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.pubmed_api import search_by_nct_id

METADATA = Path("data/metadata/studies_metadata.json")

with METADATA.open("r", encoding="utf-8") as f:
    studies = json.load(f)

for study in studies[:10]:
    nct_id = study["nct_id"]

    print(f"\nSearching PubMed for {nct_id}")

    result = search_by_nct_id(nct_id)

    ids = result["esearchresult"]["idlist"]

    if ids:
        print(f"Found PubMed IDs: {ids}")
    else:
        print("No publications found.")