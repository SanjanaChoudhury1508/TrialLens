from pathlib import Path

from docling.document_converter import DocumentConverter


class TrialDocumentParser:

    def __init__(self):
        self.converter = DocumentConverter()

    def parse(self, pdf_path: Path):
        """
        Parse a clinical trial PDF into a Docling document.
        """

        result = self.converter.convert(str(pdf_path))

        return result.document
    