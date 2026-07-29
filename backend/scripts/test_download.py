import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.pdf_downloader import download_pmc_pdf

result = download_pmc_pdf(
    "PMC9641040",
    Path("data/pdfs")
)

print(result)