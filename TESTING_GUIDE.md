# TeaL;DR Bot - Complete Testing Guide

## 📋 Prerequisites
- Bot must be invited to your Discord server
- You need appropriate permissions (Admin/Moderator for some commands)
- Server should have multiple channels for comprehensive testing

---

## 🧪 Sample Test Messages

### Step 1: Populate Your Server with Test Data
Send these messages in different channels to create searchable content:

#### #general Channel
```
Hey everyone! Just deployed the new API endpoint to production. It's working great!

The authentication system is now using JWT tokens instead of sessions.

Rate limiting is set to 100 requests per minute per user.

We should update the documentation to reflect these changes.
```

#### #bug-reports Channel
```
Found a critical bug: Database connection timeout on prod server

The user authentication is failing intermittently

Memory leak in the message processing service - needs immediate attention

    Server crashes when handling more than 1000 concurrent connections
```

#### #feature-requests Channel
```
Can we add dark mode to the dashboard?

Would love to see real-time notifications for new messages

Export functionality for chat history would be amazing

Integration with Slack would be super useful
```

#### #dev-general Channel
    ```
    Working on the new React hooks implementation

The custom hooks pattern is really clean and reusable

TypeScript types are making the codebase much more maintainable

Code review for PR #234 - looks good to merge
```

#### #announcements Channel
```
🎉 Version 2.0 is now live!

New features include: AI-powered search, real-time indexing, and analytics

Server maintenance scheduled for next Tuesday at 2 AM UTC

Welcome to all new members! Check out #rules for server guidelines
```

---

## 🔍 Testing All Commands

### 1. Search Commands

#### Test `/ask` - Natural Language Search
```
Command: /ask query: "what did @username say about the API?"
Expected: Returns relevant messages from @username about API
```

```
Command: /ask query: "authentication bugs"
Expected: Finds messages about authentication issues
```

```
Command: /ask query: "feature requests for dark mode"
Expected: Returns feature request messages about dark mode
```

#### Test `/search` - Keyword Search
```
Command: /search query: "database timeout"
Expected: Finds exact matches for "database timeout"
```

```
Command: /search query: "React hooks" channel: #dev-general
Expected: Searches only in #dev-general channel
```

```
Command: /search query: "production" user: @username
Expected: Finds messages from specific user containing "production"
```

#### Test `/recap` - Channel Summary
```
Command: /recap channel: #general timeframe: 24h
Expected: Summary of last 24 hours in #general
```

```
Command: /recap channel: #bug-reports timeframe: 7d
Expected: Weekly summary of bug reports
```

```
Command: /recap timeframe: 1h
Expected: Summary of current channel for last hour
```

---

### 2. Statistics Commands

#### Test `/stats` - Server & Personal Statistics
```
Command: /stats scope: Server Statistics
Expected: Shows server message count, active users, channels
```

```
Command: /stats scope: My Statistics
Expected: Shows your personal activity stats
```

#### Test `/trends` - Trending Topics Analysis
```
Command: /trends timeframe: 24h
Expected: Shows trending words, most active users, and active channels from last 24 hours
```

```
Command: /trends timeframe: 7d channel: #general
Expected: Shows trends specific to #general channel for last 7 days
```

```
Command: /trends timeframe: 2h
Expected: Shows recent trends from last 2 hours
```

---

### 3. Fun Commands

#### Test `/wrapped` - Year-End Summary
```
Command: /wrapped
Expected: Generates Spotify Wrapped-style summary for last year
```

```
Command: /wrapped year: 2025
Expected: Generates wrapped for specific year
```

#### Test `/timemachine` - Historical Lookup
```
Command: /timemachine date: 01-15
Expected: Shows what happened on January 15th in previous years
```

```
Command: /timemachine date: 2025-01-15
Expected: Shows what happened on specific date
```

#### Test `/quiz` - Server History Quiz
```
Command: /quiz num_questions: 5 time_period: Last 30 days
Expected: Creates 5-question quiz from last 30 days
```

---

### 4. Export & Utility Commands

#### Test `/export` - Export Search Results
```
Command: /export query: "API" format: JSON
Expected: Exports search results as JSON file
```

```
Command: /export query: "bugs" format: CSV channel: #bug-reports
Expected: Exports bug-related messages as CSV
```

#### Test `/help` - Show Help
```
Command: /help
Expected: Displays all available commands with descriptions
```

#### Test `/clear` - Clear Context
```
Command: /clear
Expected: Clears your conversation context with the bot
```

---

### 5. Admin Commands (Requires Admin Permissions)

#### Test `/settings` - Bot Settings
```
Command: /settings action: View Settings
Expected: Shows current server settings
```

```
Command: /settings action: Exclude Channel channel: #private
Expected: Excludes channel from indexing
```

```
Command: /settings action: Include Channel channel: #general
Expected: Includes channel in indexing
```

```
Command: /settings action: Set Retention Days channel: 90
Expected: Sets message retention to 90 days
```

```
Command: /settings action: Clear All Data
Expected: Clears all indexed data (requires confirmation)
```

#### Test `/customize` - Bot Personality
```
Command: /customize action: View Persona
Expected: Shows current bot personality
```

```
Command: /customize action: Set Persona persona: "You are a friendly pirate"
Expected: Changes bot personality to pirate theme
```

```
Command: /customize action: Reset Persona
Expected: Resets to default personality
```

---

## 🔍 **Quick Command Reference**

**Implemented Commands (12 total):**
- `/ask` - AI-powered semantic search
- `/recap` - Channel/user summaries
- `/stats` - Server & personal statistics
- `/trends` - Trending topics analysis
- `/wrapped` - Year-end summary
- `/timemachine` - Historical lookup
- `/quiz` - Server history quiz
- `/export` - Export search results
- `/help` - Command help
- `/clear` - Clear conversation context
- `/settings` - Bot settings (Admin)
- `/customize` - Bot personality (Admin)

**Not Implemented:**
- ~~`/search`~~ - Use `/ask` instead
- ~~`/activity`~~ - Use `/stats` instead
- ~~`/leaderboard`~~ - Not available
- ~~`/tag-*`~~ - Tag commands not available
- ~~`/summary-*`~~ - DM summary commands not available

---

## 🧪 **Advanced Testing Scenarios**

#### Test `/help` - Show Help
```
Command: /help
Expected: Displays all available commands
```

```
Command: /help command: ask
Expected: Shows detailed help for /ask command
```

#### Test `/ping` - Check Bot Status
```
Command: /ping
Expected: Shows bot latency and uptime
```

#### Test `/invite` - Get Invite Link
```
Command: /invite
Expected: Provides bot invite link
```

---

### 6. Admin Commands (Requires Admin Permissions)

#### Test `/settings` - View Settings
```
Command: /settings
Expected: Shows current server settings
```

#### Test `/settings-retention` - Set Data Retention
```
Command: /settings-retention days: 90
Expected: Sets message retention to 90 days
```

#### Test `/settings-channels` - Configure Channels
```
Command: /settings-channels action: exclude channels: #private, #admin
Expected: Excludes channels from indexing
```

```
Command: /settings-channels action: include channels: #general, #dev
Expected: Includes only specified channels
```

#### Test `/clear-data` - Clear Server Data
```
Command: /clear-data confirm: yes
Expected: Clears all indexed data (use with caution!)
```

---

## 🎯 Advanced Testing Scenarios

### Scenario 1: Cross-Channel Search
1. Send messages about "deployment" in multiple channels
2. Use `/ask query: "deployment issues"`
3. Verify results come from all channels

### Scenario 2: Time-Based Search
1. Send messages at different times
2. Use `/search query: "test" timeframe: 1h`
3. Verify only recent messages appear

### Scenario 3: User-Specific Search
1. Have multiple users discuss the same topic
2. Use `/search query: "topic" user: @specific-user`
3. Verify only that user's messages appear

### Scenario 4: Tag Workflow
1. Create tags for common responses
2. Use tags in conversations
3. Edit tags when information changes
4. Delete outdated tags

### Scenario 5: Analytics Over Time
1. Generate activity over several days
2. Check `/stats` daily
3. Compare `/trends` across different timeframes
4. Monitor `/leaderboard` changes

### Scenario 6: Summary Customization
1. Subscribe to daily summaries
2. Set topic filters
3. Receive first summary
4. Adjust topics based on relevance
5. Verify next summary reflects changes

---

## ✅ Testing Checklist

### Basic Functionality
- [ ] Bot responds to commands
- [ ] Search returns relevant results
- [ ] Messages are indexed in real-time
- [ ] Bot handles multiple simultaneous requests

### Search Accuracy
- [ ] Natural language queries work correctly
- [ ] Keyword search finds exact matches
- [ ] Channel filtering works
- [ ] User filtering works
- [ ] Time-based filtering works

### Analytics
- [ ] Stats show accurate numbers
- [ ] Activity tracking is correct
- [ ] Trends reflect actual discussion topics
- [ ] Leaderboard ranks users properly

### Tags
- [ ] Tags can be created
- [ ] Tags can be retrieved
- [ ] Tags can be edited
- [ ] Tags can be deleted
- [ ] Tag names are unique

### Summaries
- [ ] Subscription works
- [ ] DMs are received at correct time
- [ ] Topic filtering works
- [ ] Server selection works
- [ ] Unsubscribe works

### Admin Functions
- [ ] Settings can be viewed
- [ ] Retention period can be changed
- [ ] Channels can be included/excluded
- [ ] Data can be cleared

### Error Handling
- [ ] Invalid commands show helpful errors
- [ ] Missing parameters are caught
- [ ] Permission errors are clear
- [ ] Rate limiting works properly

---

## 🐛 Common Issues & Solutions

### Issue: Bot doesn't respond
**Solution:** Check bot has proper permissions (Read Messages, Send Messages, Use Slash Commands)

### Issue: Search returns no results
**Solution:** Ensure messages exist and bot has been indexing (may take a few seconds for new messages)

### Issue: Can't use admin commands
**Solution:** Verify you have Administrator or Manage Server permissions

### Issue: Summaries not received
**Solution:** Check DM settings allow messages from server members, verify subscription is active

### Issue: Tags not working
**Solution:** Ensure tag name doesn't contain spaces or special characters

---

## 📊 Performance Testing

### Load Testing
1. Send 100+ messages rapidly
2. Execute multiple search commands simultaneously
3. Monitor bot response time
4. Check for any errors or timeouts

### Stress Testing
1. Create very long messages (2000 characters)
2. Search for very common terms (thousands of results)
3. Request analytics for long timeframes (30+ days)
4. Verify bot handles gracefully

---

## 📝 Test Results Template

```
Date: [DATE]
Tester: [NAME]
Server: [SERVER NAME]

Command Tested: [COMMAND]
Input: [PARAMETERS]
Expected Result: [DESCRIPTION]
Actual Result: [DESCRIPTION]
Status: ✅ Pass / ❌ Fail
Notes: [ANY OBSERVATIONS]
```

---

## 🎓 Best Practices

1. **Test in a dedicated testing server** to avoid cluttering production
2. **Use consistent test data** for reproducible results
3. **Document any bugs** with screenshots and exact steps to reproduce
4. **Test edge cases** like empty queries, very long inputs, special characters
5. **Verify permissions** for each command type
6. **Monitor bot logs** for any errors or warnings
7. **Test across different Discord clients** (Desktop, Web, Mobile)

---

## 🚀 Quick Start Testing (5 Minutes)

If you're short on time, test these core features:

1. **Send test messages** in #general (3-4 messages)
2. **Run `/ask query: "test"`** - Verify search works
3. **Run `/recap timeframe: 1h`** - Verify summarization works
4. **Run `/stats`** - Verify analytics work
5. **Run `/tag-create name: "test" content: "testing"`** - Verify tags work
6. **Run `/ping`** - Verify bot is responsive

If all 6 pass, core functionality is working! ✅

---

## 📞 Support

If you encounter issues during testing:
- Check bot permissions
- Review error messages carefully
- Consult documentation at `/docs`
- Report bugs with detailed reproduction steps

Happy Testing! 🎉
