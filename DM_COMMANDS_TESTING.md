# Testing DM Commands - Complete Guide

## 📬 **DM Commands Overview**

Your bot has **5 DM-related commands** for managing personalized summaries and notifications:

1. `/dm-settings` - Manage DM and email preferences
2. `/request-summary` - Get on-demand summaries
3. `/bug-summary` - View recent bug discussions
4. `/summary-topics` - Filter summaries by topics
5. `/summary-servers` - Choose which servers send summaries

---

## 🚀 **Quick Start Testing**

### **Prerequisites:**
1. Bot must be running and online
2. You must be in a Discord server with the bot
3. DMs must be enabled for the server (User Settings → Privacy & Safety → Allow DMs from server members)

---

## 📝 **Step-by-Step Testing**

### **1. Test `/dm-settings` - Manage Preferences**

**⚠️ IMPORTANT: When to use the `value` parameter:**
- **Toggle actions** (Toggle DM, Toggle Email, Toggle Bug Alerts) → **NO value needed** - they automatically flip on/off
- **Set Email** → **Value REQUIRED** - enter your email address
- **Set Frequency** → **Value REQUIRED** - enter `daily`, `weekly`, or `monthly`

---

#### **View Current Settings:**
```
Command: /dm-settings action: View Settings
Expected: Shows your current DM/email preferences
```

**What you'll see:**
- ✅/❌ DM Summaries status
- ✅/❌ Email Summaries status
- ✅/❌ Bug Alerts status
- 📅 Summary frequency (daily/weekly/monthly)
- 📮 Email address (if set)

---

#### **Enable/Disable DM Summaries:**
```
Command: /dm-settings action: Toggle DM Summaries
Expected: Automatically toggles DM summaries on/off
```

**How it works:**
- If currently disabled → Enables DM summaries
- If currently enabled → Disables DM summaries
- **No value parameter needed** - it automatically toggles!
- You'll get a confirmation message showing the new state

---

#### **Set Email Address:**
```
Command: /dm-settings action: Set Email value: your.email@example.com
Expected: Sets your email for email summaries
```

**Important:**
- **Value parameter IS required** - enter your email address
- Email must be valid format (name@domain.com)
- You must set email before enabling email summaries

**Example:**
```
/dm-settings action: Set Email value: john@example.com
```

---

#### **Enable/Disable Email Summaries:**
```
Command: /dm-settings action: Toggle Email Summaries
Expected: Automatically toggles email summaries on/off
```

**Prerequisites:**
- Email address must be set first
- **No value parameter needed** - it automatically toggles!

---

#### **Set Summary Frequency:**
```
Command: /dm-settings action: Set Frequency value: daily
Expected: Sets how often you receive summaries
```

**Important:**
- **Value parameter IS required** - enter frequency
- Options: `daily`, `weekly`, or `monthly`

**Examples:**
```
/dm-settings action: Set Frequency value: daily
/dm-settings action: Set Frequency value: weekly
/dm-settings action: Set Frequency value: monthly
```

---

#### **Enable/Disable Bug Alerts:**
```
Command: /dm-settings action: Toggle Bug Alerts
Expected: Automatically toggles bug alerts on/off
```

**How it works:**
- **No value parameter needed** - it automatically toggles!
- When enabled, you'll receive alerts about critical bugs

**What it does:**
- When enabled, you'll receive alerts about critical bugs
- Useful for developers and admins

---

### **2. Test `/request-summary` - On-Demand Summaries**

**⚠️ Custom Timeframes Supported!**
You can now enter any custom timeframe like `/recap`:
- Minutes: `15m`, `30m`, `45m`
- Hours: `1h`, `2h`, `12h`, `24h`
- Days: `1d`, `3d`, `7d`, `30d`
- Weeks: `1w`, `2w`, `4w`

---

#### **Request DM Summary:**
```
Command: /request-summary time_period: 24h delivery: Send to DM
Expected: Generates summary and sends it to your DMs
```

**What happens:**
1. Bot analyzes messages from the time period
2. AI generates a comprehensive summary
3. Summary is sent to your Discord DMs
4. You get a confirmation message

**More Examples:**
```
/request-summary time_period: 2h delivery: Send to DM
/request-summary time_period: 3d delivery: Send to DM
/request-summary time_period: 1w delivery: Send to DM
```

---

#### **Request Email Summary:**
```
Command: /request-summary time_period: 7d delivery: Send to Email
Expected: Generates summary and sends it to your email
```

**Prerequisites:**
- Email must be set via `/dm-settings`
- Email summaries must be enabled

**Custom Timeframe Examples:**
```
/request-summary time_period: 12h delivery: Send to Email
/request-summary time_period: 5d delivery: Send to Email
/request-summary time_period: 2w delivery: Send to Email
```

---

### **3. Test `/bug-summary` - Bug Reports**

#### **View Recent Bugs:**
```
Command: /bug-summary days: 7
Expected: Shows summary of bugs from last 7 days
```

**What you'll see:**
- 📊 Overview: Total bugs, resolved, unresolved, critical
- ✅ Recently Resolved: List of fixed bugs
- ⚠️ Unresolved Issues: List of open bugs

**Days Range:** 1-30 days

---

### **4. Test `/summary-topics` - Topic Filtering**

#### **View Current Topics:**
```
Command: /summary-topics action: View Topics
Expected: Shows your topic filters for this server
```

**Result:**
- List of topics you're tracking
- If no topics set, you'll receive all summaries

---

#### **Add a Topic:**
```
Command: /summary-topics action: Add Topic topic: bugs
Expected: Adds "bugs" to your topic filters
```

**Examples of topics:**
- `bugs` - Bug discussions
- `features` - Feature requests
- `api` - API-related discussions
- `deployment` - Deployment updates
- `security` - Security issues

---

#### **Remove a Topic:**
```
Command: /summary-topics action: Remove Topic topic: bugs
Expected: Removes "bugs" from your filters
```

---

#### **Clear All Topics:**
```
Command: /summary-topics action: Clear All Topics
Expected: Removes all topic filters
```

**Result:** You'll receive summaries about ALL discussions again

---

### **5. Test `/summary-servers` - Server Management**

#### **View Enabled Servers:**
```
Command: /summary-servers action: View Enabled Servers
Expected: Shows which servers send you summaries
```

**What you'll see:**
- List of all servers you share with the bot
- ✅ Enabled or ❌ Disabled status for each

---

#### **Enable This Server:**
```
Command: /summary-servers action: Enable This Server
Expected: Enables summaries from the current server
```

**Use this when:** You want to receive summaries from this specific server

---

#### **Disable This Server:**
```
Command: /summary-servers action: Disable This Server
Expected: Disables summaries from the current server
```

**Use this when:** You want to stop receiving summaries from this server

---

## 🧪 **Complete Testing Workflow**

### **Scenario 1: First-Time Setup**

1. **Check current settings:**
   ```
   /dm-settings action: View Settings
   ```

2. **Enable DM summaries:**
   ```
   /dm-settings action: Toggle DM Summaries
   ```

3. **Set email (optional):**
   ```
   /dm-settings action: Set Email value: your@email.com
   ```

4. **Set frequency:**
   ```
   /dm-settings action: Set Frequency value: daily
   ```

5. **Enable this server:**
   ```
   /summary-servers action: Enable This Server
   ```

6. **Request test summary:**
   ```
   /request-summary time_period: Last 24 hours delivery: Send to DM
   ```

---

### **Scenario 2: Topic-Specific Summaries**

1. **Add topics you care about:**
   ```
   /summary-topics action: Add Topic topic: bugs
   /summary-topics action: Add Topic topic: features
   /summary-topics action: Add Topic topic: api
   ```

2. **View your topics:**
   ```
   /summary-topics action: View Topics
   ```

3. **Request filtered summary:**
   ```
   /request-summary time_period: Last 7 days delivery: Send to DM
   ```
   (Will only include messages about your topics)

---

### **Scenario 3: Bug Tracking**

1. **Enable bug alerts:**
   ```
   /dm-settings action: Toggle Bug Alerts
   ```

2. **Check recent bugs:**
   ```
   /bug-summary days: 7
   ```

3. **View bug trends:**
   ```
   /bug-summary days: 30
   ```

---

## 🔍 **Verification Checklist**

### **DM Settings:**
- [ ] Can view current settings
- [ ] Can toggle DM summaries on/off
- [ ] Can set email address
- [ ] Can toggle email summaries on/off
- [ ] Can set frequency (daily/weekly/monthly)
- [ ] Can toggle bug alerts on/off

### **Summaries:**
- [ ] Can request DM summary
- [ ] Can request email summary
- [ ] Receives summary in DM
- [ ] Receives summary in email (if configured)
- [ ] Summary contains relevant information

### **Bug Tracking:**
- [ ] Can view bug summary
- [ ] Shows resolved bugs
- [ ] Shows unresolved bugs
- [ ] Shows critical bugs

### **Topic Filtering:**
- [ ] Can view current topics
- [ ] Can add topics
- [ ] Can remove topics
- [ ] Can clear all topics
- [ ] Summaries respect topic filters

### **Server Management:**
- [ ] Can view enabled servers
- [ ] Can enable current server
- [ ] Can disable current server
- [ ] Only receives summaries from enabled servers

---

## 📧 **Testing Email Functionality**

**Note:** Email functionality requires SMTP credentials to be configured in the bot's environment variables.

### **If Email is Disabled:**
You'll see this message when starting the bot:
```
Email functionality disabled - missing SMTP credentials
```

### **To Enable Email:**
Add these to your `.env` file:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

**For Gmail:**
1. Enable 2-factor authentication
2. Generate an "App Password"
3. Use the app password (not your regular password)

---

## 🐛 **Common Issues & Solutions**

### **Issue: "Failed to send DM"**
**Solution:** 
- Check Privacy Settings → Allow DMs from server members
- Make sure you haven't blocked the bot
- Try leaving and rejoining the server

### **Issue: "No email address set"**
**Solution:**
- Run `/dm-settings action: Set Email value: your@email.com` first
- Then enable email summaries

### **Issue: "No messages found"**
**Solution:**
- Make sure there's activity in the server
- Try a longer time period (7d or 30d)
- Check that messages are being indexed (look at bot logs)

### **Issue: Email not received**
**Solution:**
- Check spam folder
- Verify email address is correct
- Check bot logs for SMTP errors
- Ensure SMTP credentials are configured

---

## 📊 **Expected Behavior**

### **DM Summary Format:**
```
📬 Server Summary - [Server Name]

🗓️ Time Period: Last 24 hours

📝 Summary:
[AI-generated summary of discussions]

🏷️ Topics Discussed:
• Topic 1
• Topic 2
• Topic 3

---
Powered by TeaL;DR Bot
```

### **Email Summary Format:**
```
Subject: [Server Name] - Summary for [Date]

Body:
- Server name
- Time period
- AI-generated summary
- List of topics
- Link back to Discord
```

---

## 🎯 **Best Practices**

1. **Start with DM summaries** before enabling email
2. **Use topic filtering** to reduce noise
3. **Set appropriate frequency** (daily for active servers, weekly for quiet ones)
4. **Enable bug alerts** if you're a developer
5. **Test with short time periods** (24h) first
6. **Disable servers** you don't want summaries from

---

## 🚨 **Important Notes**

- All DM commands respond **ephemerally** (only you can see the response)
- Summaries are generated using AI (may take 5-10 seconds)
- Email requires SMTP configuration
- Topic filtering uses keyword matching
- Bug tracking looks for bug-related keywords in messages
- Automatic summaries are sent based on your frequency setting

---

## ✅ **Quick Test Commands**

Copy and paste these to quickly test all features:

```
/dm-settings action: View Settings
/dm-settings action: Toggle DM Summaries
/summary-servers action: View Enabled Servers
/summary-servers action: Enable This Server
/summary-topics action: View Topics
/summary-topics action: Add Topic topic: test
/request-summary time_period: Last 24 hours delivery: Send to DM
/bug-summary days: 7
```

---

**Happy Testing!** 🎉

If you encounter any issues, check the bot logs for detailed error messages.
