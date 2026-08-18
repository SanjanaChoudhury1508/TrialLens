CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY,
    document_id TEXT NOT NULL,
    section TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(384),
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_document_id
ON document_chunks(document_id);