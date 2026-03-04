-- Migration: Add channel_summaries table for pre-computed hourly summaries
-- Purpose: Transform /recap quality by pre-computing summaries at write time
-- Date: March 2026
-- Priority: P1.4

-- Step 1: Create channel_summaries table
CREATE TABLE IF NOT EXISTS channel_summaries (
    id BIGSERIAL PRIMARY KEY,
    server_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    hour_bucket TIMESTAMPTZ NOT NULL,
    summary_text TEXT NOT NULL,
    message_count INT NOT NULL DEFAULT 0,
    key_topics TEXT[],
    active_users BIGINT[],
    indexed_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure one summary per server/channel/hour
    UNIQUE(server_id, channel_id, hour_bucket)
);

-- Step 2: Create indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_summaries_server_channel 
ON channel_summaries(server_id, channel_id);

CREATE INDEX IF NOT EXISTS idx_summaries_hour 
ON channel_summaries(hour_bucket DESC);

CREATE INDEX IF NOT EXISTS idx_summaries_server_hour 
ON channel_summaries(server_id, hour_bucket DESC);

-- Step 3: Create index for key topics search
CREATE INDEX IF NOT EXISTS idx_summaries_topics 
ON channel_summaries USING GIN(key_topics);

-- Step 4: Add comments for documentation
COMMENT ON TABLE channel_summaries IS 'Pre-computed hourly summaries of channel activity for fast /recap queries';
COMMENT ON COLUMN channel_summaries.hour_bucket IS 'Start of the hour (e.g., 2026-03-04 14:00:00)';
COMMENT ON COLUMN channel_summaries.summary_text IS 'AI-generated summary of messages in this hour';
COMMENT ON COLUMN channel_summaries.message_count IS 'Number of messages summarized';
COMMENT ON COLUMN channel_summaries.key_topics IS 'Array of main topics discussed';
COMMENT ON COLUMN channel_summaries.active_users IS 'Array of user IDs who were active';

-- Verification queries:
-- SELECT * FROM channel_summaries WHERE server_id = 123456 ORDER BY hour_bucket DESC LIMIT 10;
-- SELECT COUNT(*), server_id FROM channel_summaries GROUP BY server_id;
