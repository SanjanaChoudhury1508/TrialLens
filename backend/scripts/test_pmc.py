import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.pdf_downloader import get_pmc_download_links

print(get_pmc_download_links("PMC9641040"))