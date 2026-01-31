-- Add thread support to messages table
ALTER TABLE messages 
ADD COLUMN IF NOT EXISTS thread_id BIGINT,
ADD COLUMN IF NOT EXISTS is_thread_message BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS parent_message_id BIGINT;

-- Index for thread queries
CREATE INDEX IF NOT EXISTS idx_thread_id ON messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_is_thread ON messages(is_thread_message);
CREATE INDEX IF NOT EXISTS idx_parent_message ON messages(parent_message_id);
