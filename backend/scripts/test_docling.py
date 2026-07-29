import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.ingestion.parser import TrialDocumentParser

PDF = Path("data/pdfs/sample.pdf")

parser = TrialDocumentParser()

document = parser.parse(PDF)

print(document)
