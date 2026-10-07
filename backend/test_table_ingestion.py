from pathlib import Path

from app.ingestion.pdf_manager import PDFIngestionManager


PDF_PATH = Path(
    "data/sample_papers/phase3_breast_immunotherapy_trial.pdf"
)


def main():
    manager = PDFIngestionManager()

    result = manager.ingest_pdf(PDF_PATH)

    print("\n" + "=" * 70)
    print("INGESTION RESULT")
    print("=" * 70)

    print(result)


if __name__ == "__main__":
    main()