# Using Commands in DMs - Complete Guide

## 🎯 **Overview**

You can now use most bot commands directly in DMs! The bot will help you select which server to search, or you can search across all your servers at once.

---

## ✨ **Supported Commands in DMs**

### **Search & Analysis:**
- `/ask` - AI-powered semantic search
- `/recap` - Channel/user summaries
- `/trends` - Trending topics analysis
- `/request-summary` - On-demand summaries

### **How It Works:**
1. **In a server** → Commands work normally on that server
2. **In DMs without server** → Bot shows interactive server picker
3. **In DMs with server name** → Searches specified server
4. **With "all" keyword** → Searches across all your servers (multi-server search)

---

## 📝 **Usage Examples**

### **Method 1: Interactive Server Picker (Easiest)**

Simply use the command in DMs without specifying a server:

```
/ask query: "API bugs"
```

**What happens:**
1. Bot responds with a dropdown menu
2. Shows all servers you share with the bot
3. Includes "🌐 All Servers (Multi-Search)" option
4. You select which server(s) to search
5. Bot performs the search and responds

---

### **Method 2: Specify Server Name**

Include the `server_name` parameter:

```
/ask query: "API bugs" server_name: MyServer
/recap time: 24h server_name: DevTeam
/trends timeframe: 7d server_name: ProductionServer
```

**Server name matching:**
- Exact match: `MyServer`
- Partial match: `Dev` (finds "DevTeam Server")
- Case-insensitive: `myserver` works too

---

### **Method 3: Multi-Server Search**

Search across ALL your servers at once:

```
/ask query: "deployment issues" server_name: all
/ask query: "security updates" server_name: all
```

**Multi-server features:**
- Searches all servers you share with bot
- Results tagged with server name
- Aggregated and sorted by relevance
- Shows which server each result came from
- Purple embed color to indicate multi-server

---

## 🔍 **Command-Specific Examples**

### **`/ask` - Natural Language Search**

**In DM with picker:**
```
/ask query: "what did @user say about the API?"
→ [Select server from dropdown]
→ Bot searches selected server
```

**In DM with server:**
```
/ask query: "authentication bugs" server_name: Backend
→ Searches "Backend" server directly
```

**Multi-server search:**
```
/ask query: "React hooks issues" server_name: all
→ Searches all servers
→ Shows results from each server
```

---

### **`/recap` - Summaries**

**In DM with picker:**
```
/recap time: 24h
→ [Select server from dropdown]
→ Generates recap for that server
```

**In DM with server:**
```
/recap time: 7d server_name: General Chat
→ Weekly recap from "General Chat" server
```

**With user filter:**
```
/recap time: 3d user: @username server_name: DevTeam
→ 3-day recap of specific user in DevTeam server
```

---

### **`/trends` - Trending Topics**

**In DM with picker:**
```
/trends timeframe: 24h
→ [Select server from dropdown]
→ Shows trending words and active users
```

**In DM with server:**
```
/trends timeframe: 7d server_name: Community
→ Week's trends in Community server
```

---

### **`/request-summary` - On-Demand Summaries**

**In DM with picker:**
```
/request-summary time_period: 24h delivery: Send to DM
→ [Select server from dropdown]
→ Summary sent to your DMs
```

**In DM with server:**
```
/request-summary time_period: 7d delivery: Send to Email server_name: Work
→ Weekly summary from Work server sent to email
```

---

## 🌐 **Multi-Server Search Details**

### **When to Use:**
- Looking for information across multiple communities
- Don't remember which server had the discussion
- Want comprehensive results from all your servers
- Comparing discussions across servers

### **How It Works:**
1. Searches each server independently
2. Takes top 10 results per server
3. Aggregates and sorts by relevance
4. Tags each result with server name
5. Generates unified AI response

### **Example Output:**
```
🌐 Multi-Server Search Results

[AI-generated response mentioning which servers discussed what]

📊 Sources: 47 messages from 3 server(s)
🏢 Servers: DevTeam, ProductionOps, Community
```

### **Limitations:**
- Slower than single-server search (searches multiple databases)
- Limited to 10 results per server
- May hit rate limits if you're in many servers
- Some commands don't support multi-server (recap, trends)

---

## 🎛️ **Server Picker Interface**

When you use a command in DMs without specifying a server:

```
🔍 Select Server

Which server would you like to search?

Your Servers
You share 5 server(s) with me.

[Dropdown Menu]
🌐 All Servers (Multi-Search)
📁 DevTeam Server (150 members)
📁 Production Ops (89 members)
📁 Community Hub (1,234 members)
📁 Testing Ground (12 members)
📁 Personal Server (3 members)
```

**Features:**
- Shows member count for each server
- "All Servers" option at the top
- Auto-selects if you only share 1 server
- 3-minute timeout (command cancels if no selection)

---

## ⚙️ **Advanced Usage**

### **Combining Filters:**

```
/ask query: "database errors" 
     server_name: Backend
     from_date: 2026-01-01
     to_date: 2026-01-31
     min_length: 50
→ Searches Backend server for database errors in January with messages 50+ chars
```

### **Channel-Specific in DMs:**

```
/recap time: 24h 
       channel: #bug-reports
       server_name: DevTeam
→ Recap of #bug-reports channel in DevTeam server
```

**Note:** Channel parameter only works if you specify the server name (can't use with picker)

---

## 🚨 **Troubleshooting**

### **"Could not find the specified server"**
**Causes:**
- Server name typo
- You're not in that server
- Bot is not in that server

**Solutions:**
- Check server name spelling
- Use the interactive picker instead
- Verify bot is in the server

---

### **"You don't share any servers with me"**
**Cause:** You're not in any servers that have this bot

**Solution:** Invite the bot to at least one server you're in

---

### **Picker times out**
**Cause:** Didn't select a server within 3 minutes

**Solution:** Run the command again and select faster

---

### **Multi-server search is slow**
**Cause:** Searching multiple databases takes time

**Solutions:**
- Use single-server search if you know which server
- Be patient (can take 10-30 seconds for many servers)
- Reduce number of servers by leaving unused ones

---

### **Wrong server selected**
**Cause:** Autocomplete or picker selection error

**Solution:** 
- Use exact server name in `server_name` parameter
- Double-check dropdown selection before confirming

---

## 📊 **Comparison: Server vs DM Usage**

| Feature | In Server | In DM |
|---------|-----------|-------|
| **Server Selection** | Automatic (current server) | Manual (picker or parameter) |
| **Multi-Server** | ❌ Not available | ✅ Available with "all" |
| **Speed** | Fast | Slightly slower (picker step) |
| **Privacy** | Public in channel | Private DM |
| **Channel Filters** | ✅ Works normally | ⚠️ Requires server_name |
| **User Mentions** | ✅ Works normally | ⚠️ Must be in selected server |

---

## 💡 **Best Practices**

### **For Single Server:**
1. Use `server_name` parameter if you know the server
2. Saves time vs using picker
3. Example: `/ask query: "bug" server_name: Dev`

### **For Multiple Servers:**
1. Use `server_name: all` for comprehensive search
2. Good for "I don't remember where this was discussed"
3. Example: `/ask query: "new feature" server_name: all`

### **For Quick Searches:**
1. Use commands in the actual server (fastest)
2. Only use DMs when you need privacy or multi-server

### **For Regular Use:**
1. Set up `/dm-settings` for automatic summaries
2. Use `/request-summary` for on-demand updates
3. Check multiple servers at once with multi-search

---

## 🎯 **Quick Reference**

**Use in server:**
```
/ask query: "your question"
```

**Use in DM with picker:**
```
/ask query: "your question"
[Select from dropdown]
```

**Use in DM with server:**
```
/ask query: "your question" server_name: ServerName
```

**Use in DM for all servers:**
```
/ask query: "your question" server_name: all
```

---

## 🔐 **Privacy & Permissions**

- **DM commands respect server permissions** - You can only search servers you're a member of
- **Bot only accesses indexed messages** - No access to messages before bot joined
- **Results are private** - Only you see DM responses
- **Multi-server aggregates your data** - Only from servers you share with bot

---

## ✅ **Testing Checklist**

- [ ] Test `/ask` in DM with picker
- [ ] Test `/ask` in DM with server_name
- [ ] Test `/ask` in DM with server_name: all
- [ ] Test `/recap` in DM
- [ ] Test `/trends` in DM
- [ ] Test `/request-summary` in DM
- [ ] Verify picker shows all your servers
- [ ] Verify multi-server results show server names
- [ ] Test with server name that doesn't exist
- [ ] Test timeout by not selecting server

---

**Enjoy using the bot from anywhere!** 🚀

For more help, use `/help` or check the main `TESTING_GUIDE.md`.
