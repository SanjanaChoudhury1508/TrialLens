from pathlib import Path

from app.ingestion.parser import TrialDocumentParser
from app.ingestion.table_extractor import TableExtractor


PDF_PATH = Path(
    "data/sample_papers/phase3_breast_immunotherapy_trial.pdf"
)


def main():
    parser = TrialDocumentParser()
    extractor = TableExtractor()

    print("=" * 70)
    print("TABLE EXTRACTION TEST")
    print("=" * 70)

    document = parser.parse(PDF_PATH)

    print(
        f"Docling detected {len(document.tables)} tables"
    )

    tables = extractor.extract(
        document,
        document_id=PDF_PATH.stem,
    )

    print(
        f"Successfully extracted {len(tables)} tables"
    )

    for index, table in enumerate(tables, start=1):

        print("\n" + "-" * 70)
        print(f"TABLE {index}")
        print(f"ID: {table.table_id}")
        print(f"Title: {table.title}")
        print(f"Page: {table.page}")
        print(f"Headers: {table.headers}")
        print(f"Rows: {len(table.rows)}")

        for row in table.rows[:5]:
            print("  ", row)


if __name__ == "__main__":
    main()