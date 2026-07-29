import json
from pathlib import Path

RAW_FILE = Path("data/raw/studies_page1.json")

with RAW_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)

study = data["studies"][0]


def walk(obj, indent=0):
    if isinstance(obj, dict):
        for key, value in obj.items():
            print(" " * indent + key)
            walk(value, indent + 4)

    elif isinstance(obj, list):
        if obj:
            walk(obj[0], indent)


walk(study)