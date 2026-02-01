-- User preferences for DM summaries and email delivery
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id BIGINT PRIMARY KEY,
    email TEXT,
    dm_summaries_enabled BOOLEAN DEFAULT TRUE,
    email_summaries_enabled BOOLEAN DEFAULT FALSE,
    summary_frequency TEXT DEFAULT 'weekly', -- daily, weekly, monthly
    bug_alerts_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_dm_enabled ON user_preferences(dm_summaries_enabled);
CREATE INDEX IF NOT EXISTS idx_user_preferences_email_enabled ON user_preferences(email_summaries_enabled);

-- User topic preferences for filtered summaries
CREATE TABLE IF NOT EXISTS user_topic_preferences (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    server_id BIGINT NOT NULL,
    topic_keywords TEXT[] NOT NULL, -- Array of keywords/topics to track
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES user_preferences(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, server_id)
);

CREATE INDEX IF NOT EXISTS idx_user_topic_preferences_user ON user_topic_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_topic_preferences_server ON user_topic_preferences(server_id);

-- Server-specific summary settings for users
CREATE TABLE IF NOT EXISTS user_server_summary_settings (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    server_id BIGINT NOT NULL,
    summaries_enabled BOOLEAN DEFAULT TRUE,
    include_channels BIGINT[], -- Specific channels to include (null = all)
    exclude_channels BIGINT[], -- Channels to exclude
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES user_preferences(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, server_id)
);

CREATE INDEX IF NOT EXISTS idx_user_server_summary_user ON user_server_summary_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_user_server_summary_server ON user_server_summary_settings(server_id);
CREATE INDEX IF NOT EXISTS idx_user_server_summary_enabled ON user_server_summary_settings(summaries_enabled);

-- Scheduled summaries tracking
CREATE TABLE IF NOT EXISTS scheduled_dm_summaries (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    server_id BIGINT NOT NULL,
    frequency TEXT NOT NULL,
    last_sent_at TIMESTAMP,
    next_send_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES user_preferences(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_scheduled_dm_summaries_next_send ON scheduled_dm_summaries(next_send_at);
CREATE INDEX IF NOT EXISTS idx_scheduled_dm_summaries_user ON scheduled_dm_summaries(user_id);

-- Bug tracking for summaries
CREATE TABLE IF NOT EXISTS bug_discussions (
    id SERIAL PRIMARY KEY,
    server_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL,
    dependency_name TEXT,
    bug_description TEXT NOT NULL,
    severity TEXT DEFAULT 'medium', -- critical, high, medium, low
    resolution TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bug_discussions_server ON bug_discussions(server_id);
CREATE INDEX IF NOT EXISTS idx_bug_discussions_resolved ON bug_discussions(resolved);
CREATE INDEX IF NOT EXISTS idx_bug_discussions_created ON bug_discussions(created_at DESC);
