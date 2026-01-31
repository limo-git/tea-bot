-- Scheduled reports configuration
CREATE TABLE IF NOT EXISTS scheduled_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    frequency TEXT NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly')),
    time_of_day TIME NOT NULL,
    day_of_week INTEGER,  -- 0-6 for weekly reports (0 = Monday)
    day_of_month INTEGER,  -- 1-31 for monthly reports
    report_type TEXT NOT NULL CHECK (report_type IN ('activity', 'highlights', 'stats')),
    is_active BOOLEAN DEFAULT TRUE,
    created_by BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_sent_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_scheduled_reports_server ON scheduled_reports(server_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_reports_active ON scheduled_reports(is_active);
CREATE INDEX IF NOT EXISTS idx_scheduled_reports_frequency ON scheduled_reports(frequency);
