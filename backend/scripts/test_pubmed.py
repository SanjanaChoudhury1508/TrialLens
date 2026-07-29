import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.pubmed_api import search_by_nct_id

result = search_by_nct_id("NCT00000102")

print(result)