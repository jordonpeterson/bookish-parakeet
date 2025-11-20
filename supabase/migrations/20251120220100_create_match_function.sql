-- Create function to match incident embeddings using cosine similarity
CREATE OR REPLACE FUNCTION match_incident_embeddings(
    query_embedding vector(768),
    match_threshold float,
    match_count int
)
RETURNS TABLE (
    incident_id bigint,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        ie.incident_id,
        1 - (ie.embedding <=> query_embedding) as similarity
    FROM incident_embeddings ie
    WHERE 1 - (ie.embedding <=> query_embedding) > match_threshold
    ORDER BY ie.embedding <=> query_embedding ASC
    LIMIT match_count;
END;
$$;
