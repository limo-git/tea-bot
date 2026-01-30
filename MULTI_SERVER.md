# Multi-Server Support Guide

Your Discord AI Search Bot now supports multiple servers with complete data isolation and per-server settings!

---

## How Multi-Server Works

### Data Isolation
- **Messages are isolated by server**: Each server's messages are stored separately using `server_id`
- **Searches are server-specific**: `/ask` and `/recap` only search within the current server
- **Settings are per-server**: Each server has its own excluded channels and configuration

### Automatic Server Detection
- The bot automatically detects which server a command is run in
- All queries filter by `server_id` to ensure data privacy
- No cross-server data leakage

---

## Database Schema for Multi-Server

### Messages Table
Already supports multi-server with `server_id` field:
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id BIGINT UNIQUE NOT NULL,
    server_id BIGINT NOT NULL,  -- Isolates messages by server
    channel_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    author_name TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Server Settings Table (NEW)
Run this in Supabase SQL Editor to add per-server settings:

```sql
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
```

---

## Per-Server Features

### 1. Excluded Channels (Per Server)
Each server can exclude different channels:

**Server A:**
```
/settings action: Exclude channel from indexing channel: #private
```

**Server B:**
```
/settings action: Exclude channel from indexing channel: #admin-only
```

These exclusions are independent - excluding a channel in Server A doesn't affect Server B.

### 2. Message Retention (Per Server)
Each server can have different retention periods (future feature):
- Server A: Keep messages for 30 days
- Server B: Keep messages for 14 days
- Server C: Keep messages for 60 days

### 3. Independent Searches
When you run `/ask` in Server A, it only searches Server A's messages.
When you run `/ask` in Server B, it only searches Server B's messages.

---

## How Data is Isolated

### Message Indexing
```python
# When a message is sent in Server A (ID: 123456)
{
    'message_id': 789,
    'server_id': 123456,  # Server A
    'content': 'Hello world',
    ...
}

# When a message is sent in Server B (ID: 654321)
{
    'message_id': 790,
    'server_id': 654321,  # Server B
    'content': 'Hello world',
    ...
}
```

### Search Queries
All database queries filter by `server_id`:

```python
# /ask command in Server A
query = supabase.table('messages')
    .select('*')
    .eq('server_id', 123456)  # Only Server A messages
    .execute()

# /ask command in Server B
query = supabase.table('messages')
    .select('*')
    .eq('server_id', 654321)  # Only Server B messages
    .execute()
```

---

## Adding the Bot to Multiple Servers

### 1. Invite Bot to New Server
Use the same invite link you used before:
1. Go to Discord Developer Portal → Your App → OAuth2 → URL Generator
2. Select scopes: `bot`, `applications.commands`
3. Select permissions: Read Messages, Send Messages, etc.
4. Copy URL and invite to new server

### 2. Bot Auto-Configures
When the bot joins a new server:
- ✅ Automatically starts indexing messages
- ✅ Creates slash commands (`/ask`, `/recap`, `/settings`)
- ✅ Creates server settings entry in database (on first use)
- ✅ Isolates all data by server ID

### 3. Configure Per-Server Settings
In each server, run:
```
/settings action: View current settings
```

This shows settings specific to that server.

---

## Storage Considerations for Multiple Servers

### Storage Estimates
With 30-day retention per server:

**Example: 3 Servers**
- Server A (high activity): 2,000 msgs/day = ~60,000 messages = ~100 MB
- Server B (medium activity): 500 msgs/day = ~15,000 messages = ~25 MB
- Server C (low activity): 100 msgs/day = ~3,000 messages = ~5 MB
- **Total**: ~130 MB (well within 500 MB free tier)

### Cleanup is Global
The cleanup task runs across all servers:
- Deletes messages older than retention period
- Works for all servers simultaneously
- Logs total storage across all servers

### Monitoring Multi-Server Storage

Check Supabase dashboard:
```sql
-- Total messages per server
SELECT server_id, COUNT(*) as message_count
FROM messages
GROUP BY server_id
ORDER BY message_count DESC;

-- Storage by server (approximate)
SELECT 
    server_id,
    COUNT(*) as messages,
    COUNT(*) * 1000 as approx_bytes
FROM messages
GROUP BY server_id;
```

---

## Commands in Multi-Server Environment

### `/ask` - Server-Specific Search
```
# In Server A
/ask query: what did @user talk about?
→ Searches only Server A messages

# In Server B (same user)
/ask query: what did @user talk about?
→ Searches only Server B messages
```

### `/recap` - Server-Specific Recap
```
# In Server A
/recap time: Last 7 days
→ Recaps only Server A activity

# In Server B
/recap time: Last 7 days
→ Recaps only Server B activity
```

### `/settings` - Server-Specific Settings
```
# In Server A
/settings action: Exclude channel from indexing channel: #private
→ Only affects Server A

# In Server B
/settings action: View current settings
→ Shows only Server B settings
```

---

## Best Practices for Multi-Server

### 1. Set Retention Per Server Activity
High-activity servers:
```
MESSAGE_RETENTION_DAYS=14  # Shorter retention
```

Low-activity servers:
```
MESSAGE_RETENTION_DAYS=60  # Longer retention
```

### 2. Exclude Sensitive Channels Per Server
Each server admin should exclude:
- Private channels
- Admin channels
- Bot spam channels

### 3. Monitor Storage
Check which servers use most storage:
```sql
SELECT server_id, COUNT(*) as msg_count
FROM messages
GROUP BY server_id
ORDER BY msg_count DESC
LIMIT 10;
```

### 4. Test Commands in Each Server
After adding bot to a new server:
1. Send a few test messages
2. Run `/ask query: test`
3. Run `/recap time: Last 24 hours`
4. Verify results are server-specific

---

## Troubleshooting Multi-Server

### Bot sees messages from other servers
**This should never happen** - all queries filter by `server_id`. If it does:
1. Check database queries include `.eq('server_id', server_id)`
2. Verify `server_id` is being passed correctly
3. Check logs for errors

### Settings apply to wrong server
Settings are stored per `server_id` in `server_settings` table. If issues:
1. Verify `server_settings` table exists
2. Check `server_id` is correct in database
3. Review logs for the settings command

### Storage fills up quickly
With multiple servers:
1. Reduce retention period globally
2. Or implement per-server retention (future feature)
3. Exclude more channels in high-activity servers

---

## Scaling to Many Servers

### Current Limits (Free Tier)
- **Supabase**: 500 MB storage
- **Gemini API**: 5 RPM (requests per minute)
- **Render**: 750 hours/month (enough for 24/7)

### Estimated Capacity
With 30-day retention and 500 MB storage:
- **~50 low-activity servers** (100 msgs/day each)
- **~20 medium-activity servers** (500 msgs/day each)
- **~8 high-activity servers** (2,000 msgs/day each)

### If You Exceed Limits

**Storage:**
- Reduce retention to 14 days
- Upgrade Supabase to Pro ($25/month for 8 GB)

**API Rate Limits:**
- Implement request queuing
- Upgrade Gemini to paid tier
- Add cooldowns between requests

**Hosting:**
- Upgrade Render to Starter ($7/month)
- Or use Railway/Fly.io

---

## Future Enhancements

Potential multi-server features to add:

- [ ] Per-server retention periods
- [ ] Cross-server search (admin only)
- [ ] Server analytics dashboard
- [ ] Per-server rate limiting
- [ ] Server-specific AI prompts
- [ ] Bulk server configuration

---

## Summary

✅ **Your bot is fully multi-server ready!**

- Data is completely isolated by server
- Each server has independent settings
- Searches never cross server boundaries
- Storage is efficiently managed across all servers
- Easy to scale to dozens of servers

Just invite the bot to new servers and it will automatically work with full data isolation! 🎉
