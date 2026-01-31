-- Response feedback table for tracking user reactions
CREATE TABLE IF NOT EXISTS response_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    feedback_type TEXT CHECK (feedback_type IN ('positive', 'negative')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for analytics
CREATE INDEX IF NOT EXISTS idx_feedback_server_id ON response_feedback(server_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON response_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_type ON response_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON response_feedback(created_at);
