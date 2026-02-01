# Local Testing Guide for TeaL;DR Bot

## 🚨 Current Issue: Interaction Timeout

You're experiencing Discord error code 10062 ("Unknown interaction"), which means the bot is taking longer than 3 seconds to acknowledge your slash command.

---

## 🔍 **Diagnosing the Timeout Issue**

### **What I've Already Fixed:**
1. ✅ Moved `defer()` to the very first line of the command
2. ✅ Added error handling around the defer
3. ✅ Added timing logs to measure defer latency

### **Restart the Bot to Apply Latest Fix:**

```bash
# Stop the bot (Ctrl+C)
cd c:\bot\tealdr-backend
venv\Scripts\activate
python main.py
```

### **After Restart, Check the Logs:**

When you run `/ask`, look for this line in the console:
```
[INFO] Defer took X.XX seconds
```

**If you see:**
- `Defer took 0.5 seconds` → Normal, should work
- `Defer took 2.5 seconds` → High latency, but should work
- `Defer took 3.5+ seconds` → Network issue causing timeout
- `Interaction expired before defer` → Network latency > 3 seconds

---

## 🌐 **Possible Causes:**

### **1. Network Latency**
- Your connection to Discord API is slow (> 3 seconds)
- **Solution:** Test from a different network or check your internet speed

### **2. Discord API Issues**
- Discord's API might be experiencing issues
- **Check:** [Discord Status](https://discordstatus.com/)

### **3. System Performance**
- Your computer is under heavy load
- **Solution:** Close other applications, check CPU/RAM usage

### **4. Antivirus/Firewall**
- Security software might be delaying network requests
- **Solution:** Temporarily disable or whitelist Python

---

## 🧪 **Testing Steps:**

### **Step 1: Test Simple Commands First**

Try commands that don't require database/AI:

```
/ping
→ Should respond instantly

/help
→ Should show command list
```

**If these work:** The issue is specific to `/ask` command
**If these fail too:** It's a general interaction timeout issue

---

### **Step 2: Test with Minimal Query**

```
/ask query: "test"
```

Watch the console for:
```
[INFO] Defer took X.XX seconds
```

---

### **Step 3: Check Your Network**

Run this in PowerShell:
```powershell
Test-NetConnection discord.com -Port 443
```

Should show:
```
TcpTestSucceeded : True
```

---

### **Step 4: Test from Different Location**

If possible:
- Try from a different WiFi network
- Use mobile hotspot
- Test from a different computer

---

## 🛠️ **Alternative Solutions:**

### **Option 1: Increase Discord.py Timeout (Not Recommended)**

This won't fix the root cause but might help diagnose:

```python
# In main.py, add timeout parameter
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    timeout=10.0  # Increase from default 3 seconds
)
```

### **Option 2: Use Webhook Response (Workaround)**

If defer continues to fail, we can switch to webhook-based responses:

```python
# Instead of defer, respond immediately with a placeholder
await interaction.response.send_message("Searching...", ephemeral=True)
# Then edit the message with results
await interaction.edit_original_response(content="Results here")
```

---

## 📊 **Performance Benchmarks:**

**Normal timing:**
- Defer: 0.1-0.5 seconds
- Database query: 0.5-1.0 seconds
- AI response: 1.0-3.0 seconds
- Total: 2-5 seconds

**Your timing (check logs):**
- Defer: ??? seconds (this is the problem)

---

## ✅ **Quick Diagnostic Checklist:**

Run through these:

- [ ] Bot shows as "Online" in Discord
- [ ] Internet connection is stable (> 10 Mbps)
- [ ] No VPN or proxy active
- [ ] Firewall allows Python network access
- [ ] Discord API status is operational
- [ ] Other bots in server respond normally
- [ ] `/ping` command works
- [ ] Console shows "Defer took X.XX seconds" message

---

## 🎯 **Next Steps:**

1. **Restart the bot** with the latest code
2. **Run `/ask query: "test"`**
3. **Check console** for "Defer took X.XX seconds"
4. **Report back** with the timing

If defer takes > 3 seconds, the issue is network latency between your machine and Discord's API, not the bot code.

---

## 💡 **Temporary Workaround:**

While we diagnose, you can test other commands that might work:

```
/ping          → Test basic response
/help          → Test command list
/stats         → Test database query (might also timeout)
/tag-list      → Test simple database read
```

---

## 🔧 **If All Else Fails:**

Deploy the bot to a cloud service with better network:
- **Railway.app** (free tier)
- **Render.com** (free tier)
- **Heroku** (paid)
- **AWS EC2** (free tier for 12 months)

Cloud hosting typically has < 100ms latency to Discord API.

---

**Let me know the defer timing from the logs and we'll proceed from there!** 🚀
