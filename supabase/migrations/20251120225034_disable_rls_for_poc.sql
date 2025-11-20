-- Disable Row Level Security for POC demo
-- WARNING: This allows unrestricted access to tables

-- Drop existing policies
DROP POLICY IF EXISTS "Allow all operations for service role" ON incidents;
DROP POLICY IF EXISTS "Allow all operations for service role" ON incident_embeddings;

-- Disable RLS
ALTER TABLE incidents DISABLE ROW LEVEL SECURITY;
ALTER TABLE incident_embeddings DISABLE ROW LEVEL SECURITY;
