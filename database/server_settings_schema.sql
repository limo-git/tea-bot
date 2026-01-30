-- Server-specific settings table
CREATE TABLE IF NOT EXISTS server_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id BIGINT UNIQUE NOT NULL,
    server_name TEXT,
    excluded_channels BIGINT[] DEFAULT '{}',
    retention_days INTEGER DEFAULT 30,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast server lookups
CREATE INDEX IF NOT EXISTS idx_server_settings_server_id ON server_settings(server_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_server_settings_updated_at BEFORE UPDATE
    ON server_settings FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();
