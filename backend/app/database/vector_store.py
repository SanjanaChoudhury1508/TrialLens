import psycopg2
from pgvector.psycopg2 import register_vector
from psycopg2.extras import Json
from psycopg2.extras import RealDictCursor
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
                VALUES (%s,%s,%s,%s,%s,%s)
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
        
    def search(self, query_embedding, top_k=5):

        query_vector = Vector(query_embedding)
    
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
    
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
                (query_vector, query_vector, top_k),
            )
    
            return cur.fetchall()
        
    