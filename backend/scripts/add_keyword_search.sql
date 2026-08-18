-- Enable PostgreSQL full-text search support
-- using an automatically maintained generated column.

ALTER TABLE document_chunks
ADD COLUMN IF NOT EXISTS search_vector TSVECTOR
GENERATED ALWAYS AS (
    to_tsvector(
        'english',
        coalesce(document_id, '') || ' ' ||
        coalesce(section, '') || ' ' ||
        coalesce(content, '')
    )
) STORED;


CREATE INDEX IF NOT EXISTS document_chunks_search_idx
ON document_chunks
USING GIN(search_vector);