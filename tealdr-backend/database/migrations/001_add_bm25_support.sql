-- Migration: Add BM25 full-text search support to messages table
-- Purpose: Enable hybrid dense (pgvector) + sparse (BM25) search for better exact-term matching
-- Date: March 2026
-- Priority: P1.1

-- Step 1: Add tsvector column for full-text search
ALTER TABLE messages 
ADD COLUMN IF NOT EXISTS content_tsv tsvector;

-- Step 2: Create GIN index for fast full-text search
CREATE INDEX IF NOT EXISTS idx_messages_content_tsv 
ON messages USING GIN(content_tsv);

-- Step 3: Create trigger to auto-update tsvector on insert/update
CREATE OR REPLACE FUNCTION messages_content_tsv_update_trigger()
RETURNS trigger AS $$
BEGIN
    NEW.content_tsv := to_tsvector('english', COALESCE(NEW.content, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS messages_content_tsv_update ON messages;

CREATE TRIGGER messages_content_tsv_update
BEFORE INSERT OR UPDATE ON messages
FOR EACH ROW
EXECUTE FUNCTION messages_content_tsv_update_trigger();

-- Step 4: Backfill existing rows (run this separately for large tables)
-- UPDATE messages SET content_tsv = to_tsvector('english', content) WHERE content_tsv IS NULL;

-- Note: For production, run backfill in batches:
-- DO $$
-- DECLARE
--     batch_size INT := 1000;
--     offset_val INT := 0;
--     rows_updated INT;
-- BEGIN
--     LOOP
--         UPDATE messages
--         SET content_tsv = to_tsvector('english', content)
--         WHERE id IN (
--             SELECT id FROM messages 
--             WHERE content_tsv IS NULL 
--             LIMIT batch_size
--         );
--         
--         GET DIAGNOSTICS rows_updated = ROW_COUNT;
--         EXIT WHEN rows_updated = 0;
--         
--         RAISE NOTICE 'Updated % rows', rows_updated;
--         PERFORM pg_sleep(0.1); -- Prevent overwhelming the database
--     END LOOP;
-- END $$;

-- Verification queries:
-- SELECT COUNT(*) FROM messages WHERE content_tsv IS NULL; -- Should be 0 after backfill
-- SELECT * FROM messages WHERE content_tsv @@ to_tsquery('english', 'docker & deployment') LIMIT 5;
