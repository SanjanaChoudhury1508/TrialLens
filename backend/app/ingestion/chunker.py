import uuid

from app.chunk_models import DocumentChunk


class SemanticChunker:

    def chunk(
        self,
        document,
        document_id=None,
    ) -> list[DocumentChunk]:
        """
        Convert a DoclingDocument into DocumentChunk objects.

        Text content is converted into semantic chunks.
        Tables are intentionally skipped here and handled by the
        dedicated table extraction pipeline.
        """

        chunks = []

        if document_id is None:
            document_id = "PDF_DOCUMENT"

        current_section = "Document"

        for item, _level in document.iterate_items():

            # -------------------------------------------------
            # Identify the Docling item type
            # -------------------------------------------------

            label = getattr(item, "label", None)

            label_name = ""

            if label is not None:
                label_name = getattr(
                    label,
                    "value",
                    str(label),
                ).lower()

            # Tables are handled separately.
            if label_name == "table":
                continue

            # -------------------------------------------------
            # Only process items that contain text
            # -------------------------------------------------

            if not hasattr(item, "text"):
                continue

            text = item.text.strip()

            if not text:
                continue

            # -------------------------------------------------
            # Use headings as section names
            # -------------------------------------------------

            if label_name in {
                "title",
                "section_header",
                "heading",
            }:
                current_section = text
                continue

            # -------------------------------------------------
            # Get page number when available
            # -------------------------------------------------

            page = None

            if getattr(item, "prov", None):
                try:
                    page = item.prov[0].page_no
                except (
                    AttributeError,
                    IndexError,
                ):
                    page = None

            # -------------------------------------------------
            # Create text chunk
            # -------------------------------------------------

            chunks.append(
                DocumentChunk(
                    chunk_id=str(uuid.uuid4()),
                    document_id=document_id,
                    section=current_section,
                    text=text,
                    page=page,
                    metadata={
                        "source": "pdf",
                        "docling_label": (
                            str(label)
                            if label
                            else None
                        ),
                    },
                )
            )

        return chunks

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 600,
        overlap: int = 100,
    ) -> list[str]:
        """
        Split plain text into overlapping chunks.
        """

        chunks = []

        if not text:
            return chunks

        start = 0
        step = chunk_size - overlap

        while start < len(text):

            end = min(
                start + chunk_size,
                len(text),
            )

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end == len(text):
                break

            start += step

        return chunks