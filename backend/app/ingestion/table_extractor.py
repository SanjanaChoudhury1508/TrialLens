from __future__ import annotations

from app.document_structure import DocumentTable


class TableExtractor:
    """
    Extract structured tables from a DoclingDocument.

    Tables are intentionally kept separate from prose chunks so
    that they can later be handled by a dedicated Table QA stage.
    """

    @staticmethod
    def _get_page(table):
        provenance = getattr(table, "prov", None)

        if not provenance:
            return None

        try:
            return provenance[0].page_no
        except (AttributeError, IndexError):
            return None

    @staticmethod
    def _get_title(table, document):
        try:
            title = table.caption_text(document)

            if title:
                return title.strip()
        except Exception:
            pass

        return None

    @staticmethod
    def _make_unique_headers(headers: list[str]) -> list[str]:
        """
        Ensure column names are non-empty and unique.
        """

        result = []
        seen = {}

        for index, header in enumerate(headers):
            header = str(header).strip()

            if not header:
                header = f"column_{index + 1}"

            count = seen.get(header, 0)

            if count:
                unique_header = f"{header}_{count + 1}"
            else:
                unique_header = header

            seen[header] = count + 1
            result.append(unique_header)

        return result

    def extract(
        self,
        document,
        document_id: str,
    ) -> list[DocumentTable]:

        tables: list[DocumentTable] = []

        table_number = 0

        for index, table in enumerate(document.tables):

            # ---------------------------------------------
            # Identify table title/caption
            # ---------------------------------------------

            title = self._get_title(
                table,
                document,
            )

            # ---------------------------------------------
            # Skip figure/chart content that Docling may
            # have represented as a table.
            # ---------------------------------------------

            if title:

                normalized_title = title.strip().lower()

                if (
                    normalized_title.startswith("figure ")
                    or normalized_title.startswith("fig. ")
                    or normalized_title.startswith("fig ")
                ):
                    print(
                        f"⚠ Skipping visual content detected "
                        f"as table: {title}"
                    )
                    continue

            # ---------------------------------------------
            # Export structured table
            # ---------------------------------------------

            try:
                dataframe = table.export_to_dataframe(
                    doc=document
                )

            except Exception as exc:
                print(
                    f"⚠ Failed to export table {index + 1}: {exc}"
                )
                continue

            if dataframe.empty:
                continue

            dataframe = dataframe.fillna("")

            # ---------------------------------------------
            # Normalize headers
            # ---------------------------------------------

            headers = self._make_unique_headers(
                [
                    str(column)
                    for column in dataframe.columns
                ]
            )
            # ---------------------------------------------
            # Recover table caption when Docling places it
            # inside the first dataframe column header.
            # ---------------------------------------------

            if headers and headers[0].lower().startswith("table "):
                if title is None:
                    title = headers[0]

                headers[0] = "Characteristic"
            # ---------------------------------------------
            # Convert rows to JSON-compatible strings
            # ---------------------------------------------

            rows = []

            for row in dataframe.itertuples(
                index=False,
                name=None,
            ):
                rows.append(
                    [
                        str(value).strip()
                        for value in row
                    ]
                )

            # ---------------------------------------------
            # Create stable table ID
            # ---------------------------------------------

            table_number += 1

            table_id = (
                f"{document_id}::table::{table_number}"
            )

            table_metadata = {
                "source": "pdf_table",
                "docling_ref": getattr(
                    table,
                    "self_ref",
                    None,
                ),
                "row_count": len(rows),
                "column_count": len(headers),
            }

            tables.append(
                DocumentTable(
                    table_id=table_id,
                    document_id=document_id,
                    title=title,
                    headers=headers,
                    rows=rows,
                    page=self._get_page(table),
                    metadata=table_metadata,
                )
            )

        return tables
