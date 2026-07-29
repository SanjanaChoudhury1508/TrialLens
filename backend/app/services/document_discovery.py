from pathlib import Path
import json


def load_metadata(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_documents(documents, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            [doc.to_dict() for doc in documents],
            f,
            indent=2,
        )