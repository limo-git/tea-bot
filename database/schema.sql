-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id BIGINT UNIQUE NOT NULL,
    server_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    author_name TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX idx_server_channel ON messages(server_id, channel_id);
CREATE INDEX idx_author_id ON messages(author_id);
CREATE INDEX idx_created_at ON messages(created_at);
CREATE INDEX idx_message_id ON messages(message_id);

-- Create index for vector similarity search
CREATE INDEX ON messages USING ivfflat (embedding vector_cosine_ops);
