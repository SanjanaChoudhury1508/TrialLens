import json
from pathlib import Path

from app.document_models import TrialDocument


class DocumentLoader:

    def __init__(self, index_path: Path):
        self.index_path = index_path

    def load(self) -> list[TrialDocument]:
        """
        Load all discovered documents from document_index.json
        """

        with self.index_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        documents = []

        for item in data:
            documents.append(
                TrialDocument(**item)
            )

        return documents