import re

import psycopg2
from pgvector.psycopg2 import register_vector
from psycopg2.extras import RealDictCursor
from pgvector import Vector

from app.config import settings


class CloudVectorStore:

    def __init__(self):
        if not settings.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL is required in cloud mode."
            )

        self.conn = psycopg2.connect(settings.DATABASE_URL)

        with self.conn.cursor() as cur:
            cur.execute("SET search_path TO public")

        register_vector(self.conn)

    # =====================================================
    # VECTOR SEARCH — GEMINI 768-DIMENSION EMBEDDINGS
    # =====================================================

    def search(self, query_embedding, top_k: int = 5):

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
                FROM cloud_document_chunks
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s
                LIMIT %s;
                """,
                (query_vector, query_vector, top_k),
            )

            results = cur.fetchall()

        return self._enrich_results(results)

    # =====================================================
    # KEYWORD SEARCH
    # =====================================================

    
    def keyword_search(self, query: str, top_k: int = 5):

        # Extract searchable terms and remove common stop words.
        stop_words = {
            "what", "are", "the", "of", "in", "for",
            "and", "or", "is", "was", "were", "a",
            "an", "to", "with", "on", "by", "from",
            "about", "which", "who", "how"
        }

        terms = [
            term.lower()
            for term in re.findall(r"[a-zA-Z0-9]+", query)
            if len(term) >= 3 and term.lower() not in stop_words
        ]

        # Preserve order while removing duplicates.
        terms = list(dict.fromkeys(terms))

        if not terms:
            return []

        # OR-based matching instead of requiring all terms.
        tsquery = " | ".join(terms)

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
                        to_tsquery('english', %s)
                    ) AS keyword_score
                FROM public.cloud_document_chunks
                WHERE search_vector @@
                    to_tsquery('english', %s)
                ORDER BY keyword_score DESC
                LIMIT %s;
                """,
                (tsquery, tsquery, top_k),
            )

            results = cur.fetchall()

        enriched = self._enrich_results(results)

        for result, row in zip(enriched, results):
            result["keyword_score"] = row["keyword_score"]

        return enriched


    # =====================================================
    # STRUCTURED TABLE SEARCH
    # Uses the existing document_tables table.
    # =====================================================

    def search_tables(
        self,
        query: str,
        top_k: int = 5,
        trial_id: str | None = None,
    ):

        query = query.strip()

        if not query:
            return []

        terms = [
            term.lower()
            for term in re.findall(r"\b[a-zA-Z0-9]+\b", query)
            if len(term) >= 3
        ]

        if not terms:
            return []

        conditions = []

        for _ in terms:
            conditions.append(
                """
                (
                    title ILIKE %s
                    OR headers::text ILIKE %s
                    OR rows::text ILIKE %s
                )
                """
            )

        where_terms = " OR ".join(conditions)

        parameters = []

        for term in terms:
            pattern = f"%{term}%"
            parameters.extend([pattern, pattern, pattern])

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
                WHERE trial_id = %s
                  AND ({where_terms})
                ORDER BY page NULLS LAST
                LIMIT %s;
            """

            parameters.insert(0, trial_id.upper())

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
                WHERE ({where_terms})
                ORDER BY page NULLS LAST
                LIMIT %s;
            """

        parameters.append(top_k)

        with self.conn.cursor(
            cursor_factory=RealDictCursor
        ) as cur:

            cur.execute(sql, parameters)
            results = cur.fetchall()

        return [dict(row) for row in results]

    # =====================================================
    # RESULT ENRICHMENT
    # Preserves the original VectorStore result structure.
    # =====================================================

    def _enrich_results(self, results):

        enriched_results = []

        for row in results:

            document_id = row["document_id"]
            content = row["content"] or ""
            metadata = row["metadata"] or {}

            if document_id.upper().startswith("NCT"):

                source_type = "ClinicalTrials.gov"
                trial_id = document_id.upper()

            else:

                source_type = "Clinical PDF"
                trial_id = metadata.get("trial_id")

                if trial_id:
                    trial_id = trial_id.upper()

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

            if "distance" in row:
                result["distance"] = row["distance"]

            if "keyword_score" in row:
                result["keyword_score"] = row["keyword_score"]

            enriched_results.append(result)

        return enriched_results

    # =====================================================
    # CONNECTION CLEANUP
    # =====================================================

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
