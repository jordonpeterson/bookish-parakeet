-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;

-- Create incident_embeddings table
CREATE TABLE IF NOT EXISTS incident_embeddings (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    embedding vector(768) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(incident_id)
);

-- Create HNSW index for fast similarity search
-- m=16 (max connections per layer) and ef_construction=64 are good defaults
CREATE INDEX incident_embeddings_embedding_idx
    ON incident_embeddings
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Enable Row Level Security
ALTER TABLE incident_embeddings ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations for service role
CREATE POLICY "Allow all operations for service role"
    ON incident_embeddings
    FOR ALL
    USING (true);
