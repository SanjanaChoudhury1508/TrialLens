CREATE TABLE IF NOT EXISTS document_tables (
    table_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    trial_id TEXT,
    title TEXT,
    headers JSONB NOT NULL DEFAULT '[]'::jsonb,
    rows JSONB NOT NULL DEFAULT '[]'::jsonb,
    page INTEGER,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS document_tables_document_idx
ON document_tables(document_id);

CREATE INDEX IF NOT EXISTS document_tables_trial_idx
ON document_tables(trial_id);