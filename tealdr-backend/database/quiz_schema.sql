-- Quiz sessions and leaderboard
CREATE TABLE IF NOT EXISTS quiz_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id BIGINT NOT NULL,
    created_by BIGINT NOT NULL,
    num_questions INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS quiz_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES quiz_sessions(id),
    server_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    user_name TEXT NOT NULL,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    completed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_server ON quiz_sessions(server_id);
CREATE INDEX IF NOT EXISTS idx_quiz_scores_session ON quiz_scores(session_id);
CREATE INDEX IF NOT EXISTS idx_quiz_scores_server ON quiz_scores(server_id);
CREATE INDEX IF NOT EXISTS idx_quiz_scores_user ON quiz_scores(user_id);
