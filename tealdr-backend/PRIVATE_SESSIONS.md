# Private Sessions Feature

## Overview
Private sessions allow server administrators to temporarily disable message indexing for specific channels. This is useful for:
- Private discussions that shouldn't be searchable
- Sensitive conversations
- Temporary confidential meetings
- Testing without polluting the index

## Usage

### Start a Private Session
```
/private_session action:Start Private Session channel:#channel-name duration:60
```
- **channel**: The channel to make private
- **duration**: Duration in minutes (e.g., 30, 60, 120)

**Example:**
```
/private_session action:Start Private Session channel:#executive-chat duration:120
```

This will:
- ✅ Disable message indexing for #executive-chat
- ⏱️ Set a 120-minute timer
- 🔒 Messages sent during this time won't be indexed
- 📝 Auto-expire after 2 hours

### Stop a Private Session Early
```
/private_session action:Stop Private Session channel:#channel-name
```

This will:
- ✅ Immediately end the private session
- 🔓 Re-enable message indexing
- 📝 New messages will be indexed normally

### List Active Sessions
```
/private_session action:List Active Sessions
```

Shows:
- All active private sessions in the server
- Time remaining for each
- Who started each session
- When they expire

## How It Works

### During a Private Session
1. **Messages are NOT indexed** - They won't appear in `/ask`, `/lookup`, or `/recap` results
2. **Automatic expiry** - Session ends automatically after the specified duration
3. **Manual override** - Admins can stop sessions early
4. **Background cleanup** - Expired sessions are automatically removed

### After a Private Session
1. **Indexing resumes** - New messages are indexed normally
2. **Old messages remain private** - Messages sent during the session are never indexed
3. **No retroactive indexing** - Past messages aren't indexed after the session ends

## Technical Details

### Storage
- Sessions are stored in-memory (not persisted to database)
- Sessions are lost on bot restart
- Cleanup task runs every minute to remove expired sessions

### Permissions
- **Admin only** - Only server administrators can manage private sessions
- **Per-channel** - Each channel can have its own independent session
- **Server-scoped** - Sessions are specific to each server

### Integration
- **Message indexing** - `bot/events.py` checks for active sessions before indexing
- **Background jobs** - Chunker job also respects private sessions
- **Real-time** - Takes effect immediately when started

## Examples

### 1-hour executive meeting
```
/private_session action:Start channel:#executive-board duration:60
```

### 30-minute sensitive discussion
```
/private_session action:Start channel:#hr-private duration:30
```

### Stop early
```
/private_session action:Stop channel:#executive-board
```

### Check all active sessions
```
/private_session action:List
```

## Limitations

1. **Not retroactive** - Doesn't affect already-indexed messages
2. **Memory-only** - Sessions lost on bot restart
3. **No database persistence** - Sessions aren't saved
4. **Manual management** - Admins must remember to start/stop

## Future Enhancements

Potential improvements:
- [ ] Persist sessions to database
- [ ] Scheduled sessions (start at specific time)
- [ ] Recurring sessions (daily/weekly patterns)
- [ ] Retroactive un-indexing (remove already-indexed messages)
- [ ] Role-based access (allow specific roles to manage sessions)
- [ ] Session templates (preset durations/channels)
