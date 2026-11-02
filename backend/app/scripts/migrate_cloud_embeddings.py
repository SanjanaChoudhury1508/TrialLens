import argparse
import json
import time

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from pgvector import Vector
from pgvector.psycopg2 import register_vector

from app.config import settings
from app.services.gemini_embedding_service import GeminiEmbeddingService


BATCH_SIZE = 8
MODEL_DIMENSIONS = 768


def connect():
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured.")

    conn = psycopg2.connect(settings.DATABASE_URL)
    conn.autocommit = False
    register_vector(conn)

    with conn.cursor() as cur:
        cur.execute("SET search_path TO public")

    conn.commit()
    return conn


def embed_batch(service, texts):
    """Generate document embeddings with limited retries."""
    for attempt in range(3):
        try:
            response = service.client.models.embed_content(
                model=service.MODEL_NAME,
                contents=texts,
                config=service._document_config(),
            )

            embeddings = [
                item.values for item in response.embeddings
            ]

            if len(embeddings) != len(texts):
                raise RuntimeError(
                    f"Expected {len(texts)} embeddings, "
                    f"received {len(embeddings)}."
                )

            for embedding in embeddings:
                if len(embedding) != MODEL_DIMENSIONS:
                    raise RuntimeError("Unexpected embedding dimensions.")

            return embeddings

        except Exception as exc:
            message = str(exc).lower()

            if "quota" in message or "billing" in message:
                raise RuntimeError(
                    "Gemini quota/billing restriction. "
                    "Stopping migration; no further retries."
                ) from exc

            if attempt == 2:
                raise

            wait = 2 ** (attempt + 1)
            print(f"Embedding request failed. Retrying in {wait}s...")
            time.sleep(wait)


def migrate(limit, batch_size, dry_run):
    conn = connect()
    service = GeminiEmbeddingService()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    source.id,
                    source.document_id,
                    source.section,
                    source.content,
                    source.metadata
                FROM public.document_chunks AS source
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM public.cloud_document_chunks AS target
                    WHERE target.id = source.id
                )
                ORDER BY source.id
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()

        print(f"Chunks available for migration: {len(rows)}")

        if not rows:
            print("Nothing to migrate.")
            return

        if dry_run:
            print("Dry run: no embeddings generated and no rows inserted.")
            return

        migrated = 0

        for start in range(0, len(rows), batch_size):
            batch = rows[start:start + batch_size]
            texts = [row["content"] for row in batch]

            embeddings = embed_batch(service, texts)

            with conn.cursor() as cur:
                for row, embedding in zip(batch, embeddings):
                    cur.execute(
                        """
                        INSERT INTO public.cloud_document_chunks (
                            id,
                            document_id,
                            section,
                            content,
                            embedding,
                            metadata
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                        """,
                        (
                            row["id"],
                            row["document_id"],
                            row["section"],
                            row["content"],
                            Vector(embedding),
                            Json(row["metadata"] or {}),
                        ),
                    )

            conn.commit()
            migrated += len(batch)
            print(f"Migrated {migrated}/{len(rows)} chunks.")
            time.sleep(45)

        print("Migration batch completed.")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.limit < 1 or args.batch_size < 1:
        parser.error("--limit and --batch-size must be positive.")

    migrate(args.limit, args.batch_size, args.dry_run)