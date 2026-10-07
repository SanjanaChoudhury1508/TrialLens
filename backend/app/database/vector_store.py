import re

import psycopg2
from pgvector.psycopg2 import register_vector
from psycopg2.extras import Json, RealDictCursor
from pgvector import Vector

from app.config import settings
from app.chunk_models import DocumentChunk


class VectorStore:

    def __init__(self):

        self.conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
        )

        register_vector(self.conn)

    # =========================================================
    # INSERT
    # =========================================================

    def insert_chunk(
        self,
        chunk: DocumentChunk,
        embedding: list[float],
    ):

        with self.conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO document_chunks
                (
                    id,
                    document_id,
                    section,
                    content,
                    embedding,
                    metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    chunk.chunk_id,
                    chunk.document_id,
                    chunk.section,
                    chunk.text,
                    embedding,
                    Json(chunk.metadata),
                ),
            )

        self.conn.commit()

   # =========================================================
   # INSERT TABLE
   # =========================================================

    def insert_table(self, table, trial_id=None):
        with self.conn.cursor() as cur:
            metadata = dict(table.metadata or {})

            if trial_id:
                metadata["trial_id"] = trial_id

            cur.execute(
                """
                INSERT INTO document_tables
                (
                    table_id,
                    document_id,
                    trial_id,
                    title,
                    headers,
                    rows,
                    page,
                    metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (table_id)
                DO UPDATE SET
                    document_id = EXCLUDED.document_id,
                    trial_id = EXCLUDED.trial_id,
                    title = EXCLUDED.title,
                    headers = EXCLUDED.headers,
                    rows = EXCLUDED.rows,
                    page = EXCLUDED.page,
                    metadata = EXCLUDED.metadata
                """,
                (
                    table.table_id,
                    table.document_id,
                    trial_id,
                    table.title,
                    Json(table.headers),
                    Json(table.rows),
                    table.page,
                    Json(metadata),
                ),
            )

        self.conn.commit()

    # =========================================================
    # DELETE TABLE
    # =========================================================
    def delete_document_tables(self, document_id):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM document_tables
                WHERE document_id = %s;
                """,
                (document_id,),
            )

            deleted = cur.rowcount

        self.conn.commit()

        return deleted

        # =========================================================
    # TABLE SEARCH
    # =========================================================

    def search_tables(
        self,
        query: str,
        top_k: int = 5,
        trial_id: str | None = None,
    ):
        """
        Search structured document tables using
        token-based PostgreSQL text matching.

        Tables remain separate from document_chunks.
        """

        query = query.strip()

        if not query:
            return []

        # Split the question into useful search terms.
        terms = [
            term.lower()
            for term in re.findall(r"\b[a-zA-Z0-9]+\b", query)
            if len(term) >= 3
        ]

        if not terms:
            return []

        # Build one condition for each term.
        term_conditions = []

        for _ in terms:
            term_conditions.append(
                """
                (
                    title ILIKE %s
                    OR headers::text ILIKE %s
                    OR rows::text ILIKE %s
                )
                """
            )

        where_terms = " OR ".join(term_conditions)

        parameters = []

        for term in terms:
            pattern = f"%{term}%"
            parameters.extend(
                [pattern, pattern, pattern]
            )

        if trial_id:

            sql = f"""
                SELECT
                    table_id,
                    document_id,
                    trial_id,
                    title,
                    headers,
                    rows,
                    page,
                    metadata
                FROM document_tables
                WHERE
                    trial_id = %s
                    AND ({where_terms})
                ORDER BY page NULLS LAST
                LIMIT %s;
            """

            parameters.insert(0, trial_id.upper())
            parameters.append(top_k)

        else:

            sql = f"""
                SELECT
                    table_id,
                    document_id,
                    trial_id,
                    title,
                    headers,
                    rows,
                    page,
                    metadata
                FROM document_tables
                WHERE
                    ({where_terms})
                ORDER BY page NULLS LAST
                LIMIT %s;
            """

            parameters.append(top_k)

        with self.conn.cursor(
            cursor_factory=RealDictCursor
        ) as cur:

            cur.execute(
                sql,
                parameters,
            )

            results = cur.fetchall()

        return [dict(row) for row in results]

    # =========================================================
    # DELETE DOCUMENT
    # =========================================================

    def delete_document(
        self,
        document_id: str,
    ):
        """
        Delete all chunks belonging to a document.

        Used before re-indexing a PDF to prevent
        duplicate chunks.
        """

        with self.conn.cursor() as cur:

            cur.execute(
                """
                DELETE FROM document_chunks
                WHERE document_id = %s;
                """,
                (document_id,),
            )

            deleted = cur.rowcount

        self.conn.commit()

        if deleted > 0:

            print(
                f"✓ Removed {deleted} existing chunks "
                f"for {document_id}"
            )

        return deleted

    # =========================================================
    # VECTOR SEARCH
    # =========================================================

    def search(
        self,
        query_embedding,
        top_k: int = 5,
    ):
        """
        Dense semantic search using pgvector.
        """

        query_vector = Vector(query_embedding)

        with self.conn.cursor(
            cursor_factory=RealDictCursor
        ) as cur:

            cur.execute(
                """
                SELECT
                    document_id,
                    section,
                    content,
                    metadata,
                    embedding <=> %s AS distance
                FROM document_chunks
                ORDER BY embedding <=> %s
                LIMIT %s;
                """,
                (
                    query_vector,
                    query_vector,
                    top_k,
                ),
            )

            results = cur.fetchall()

        return self._enrich_results(results)

    # =========================================================
    # KEYWORD SEARCH
    # =========================================================

    def keyword_search(
        self,
        query: str,
        top_k: int = 5,
    ):
        """
        PostgreSQL full-text keyword search.

        Uses the generated search_vector column
        and GIN index.
        """

        with self.conn.cursor(
            cursor_factory=RealDictCursor
        ) as cur:

            cur.execute(
                """
                SELECT
                    document_id,
                    section,
                    content,
                    metadata,
                    ts_rank(
                        search_vector,
                        websearch_to_tsquery(
                            'english',
                            %s
                        )
                    ) AS keyword_score
                FROM document_chunks
                WHERE search_vector @@
                    websearch_to_tsquery(
                        'english',
                        %s
                    )
                ORDER BY keyword_score DESC
                LIMIT %s;
                """,
                (
                    query,
                    query,
                    top_k,
                ),
            )

            results = cur.fetchall()

        enriched_results = self._enrich_results(
            results
        )

        for result, row in zip(
            enriched_results,
            results,
        ):

            result["keyword_score"] = (
                row["keyword_score"]
            )

        return enriched_results

    # =========================================================
    # RESULT ENRICHMENT
    # =========================================================

    def _enrich_results(
        self,
        results,
    ):
        """
        Adds source type and NCT trial ID
        information to retrieval results.
        """

        enriched_results = []

        for row in results:

            document_id = row["document_id"]

            content = row["content"] or ""

            metadata = row["metadata"] or {}

            # ---------------------------------------------
            # Determine source type and trial identity
            # ---------------------------------------------

            if document_id.upper().startswith("NCT"):

                source_type = "ClinicalTrials.gov"
                trial_id = document_id.upper()

            else:

                source_type = "Clinical PDF"

                # Prefer structured metadata from ingestion.
                trial_id = metadata.get("trial_id")

                if trial_id:
                    trial_id = trial_id.upper()

                # Fall back to detecting an NCT ID
                # inside the retrieved chunk.
                if not trial_id:

                    match = re.search(
                        r"\bNCT\d{8}\b",
                        content,
                        re.IGNORECASE,
                    )

                    if match:
                        trial_id = match.group(0).upper()

            result = {
                "document_id": document_id,
                "source_type": source_type,
                "trial_id": trial_id,
                "section": row["section"],
                "content": content,
                "metadata": metadata,
            }

            # Preserve vector distance
            if "distance" in row:

                result["distance"] = (
                    row["distance"]
                )

            # Preserve keyword score
            if "keyword_score" in row:

                result["keyword_score"] = (
                    row["keyword_score"]
                )

            enriched_results.append(result)

        return enriched_results
