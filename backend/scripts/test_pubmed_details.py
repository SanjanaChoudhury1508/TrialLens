import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.pubmed_api import (
    search_by_nct_id,
    fetch_article_details,
)

nct = "NCT02392455"

search = search_by_nct_id(nct)

ids = search["esearchresult"]["idlist"]

print("PubMed IDs:", ids)

details = fetch_article_details(ids)

print(details)