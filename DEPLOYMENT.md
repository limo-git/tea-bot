# 24/7 Deployment Guide

This guide covers deploying your Discord bot to run 24/7 on free/cheap hosting platforms.

---

## Storage Optimization

The bot now includes automatic cleanup to manage Supabase storage:

### Configuration (in `.env`)

```env
MESSAGE_RETENTION_DAYS=30      # Keep messages for 30 days (adjust as needed)
CLEANUP_INTERVAL_HOURS=24      # Run cleanup every 24 hours
```

### How It Works

- **Automatic Cleanup**: Every 24 hours, messages older than 30 days are deleted
- **Storage Monitoring**: Logs current storage usage after each cleanup
- **Configurable Retention**: Adjust retention period based on your needs

### Storage Estimates

With 30-day retention on an active server:
- **Low activity** (100 msgs/day): ~3,000 messages = ~5 MB
- **Medium activity** (500 msgs/day): ~15,000 messages = ~25 MB
- **High activity** (2,000 msgs/day): ~60,000 messages = ~100 MB

Supabase free tier: **500 MB** - plenty of space!

### Manual Cleanup

To manually trigger cleanup, add this command to your bot or run in Python:

```python
from utils.cleanup import cleanup_old_messages
from database.supabase_client import supabase_client
await cleanup_old_messages(supabase_client)
```

---

## Option 1: Render.com (Recommended - Free Tier)

### Pros
- ✅ Free tier available
- ✅ Easy setup with GitHub
- ✅ Automatic deployments
- ✅ Good uptime

### Cons
- ⚠️ Free tier spins down after 15 min inactivity (but Discord bots stay active)
- ⚠️ 750 hours/month free (enough for 24/7)

### Setup Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/discord-ai-bot.git
   git push -u origin main
   ```

2. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

3. **Create New Web Service**
   - Click "New +" → "Background Worker"
   - Connect your GitHub repository
   - Name: `discord-ai-bot`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`

4. **Add Environment Variables**
   Go to Environment tab and add:
   ```
   DISCORD_BOT_TOKEN=your_token
   SUPABASE_PROJECT_URL=your_url
   SUPABASE_PUBLISHABLE_KEY=your_key
   SUPABASE_SECRET_KEY=your_secret
   GEMINI_API_KEY=your_key
   EXCLUDED_CHANNELS=
   LOG_LEVEL=INFO
   MESSAGE_RETENTION_DAYS=30
   CLEANUP_INTERVAL_HOURS=24
   ```

5. **Deploy**
   - Click "Create Background Worker"
   - Render will automatically deploy
   - Check logs to verify bot is running

### Using render.yaml (Alternative)

The included `render.yaml` file allows one-click deployment:

1. Push code to GitHub
2. Go to Render Dashboard
3. Click "New +" → "Blueprint"
4. Connect repository
5. Render reads `render.yaml` and sets everything up
6. Just add your environment variable values

---

## Option 2: Railway.app (Easy Setup)

### Pros
- ✅ $5 free credit monthly
- ✅ Very easy setup
- ✅ Great developer experience
- ✅ No sleep/spin-down

### Cons
- ⚠️ Free credit runs out (~140 hours on free tier)
- ⚠️ Need credit card for verification

### Setup Steps

1. **Push to GitHub** (same as Render)

2. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

3. **Deploy from GitHub**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway auto-detects Python and uses `railway.json`

4. **Add Environment Variables**
   - Click on your service
   - Go to "Variables" tab
   - Add all environment variables (same as Render)

5. **Deploy**
   - Railway automatically deploys
   - Check logs in dashboard

---

## Option 3: Fly.io (Advanced)

### Pros
- ✅ Generous free tier
- ✅ Good performance
- ✅ Global deployment

### Cons
- ⚠️ Requires credit card
- ⚠️ More complex setup

### Setup Steps

1. **Install Fly CLI**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Create fly.toml**
   ```bash
   fly launch
   ```
   
   Answer prompts:
   - App name: `discord-ai-bot-yourname`
   - Region: Choose closest to you
   - Database: No
   - Deploy now: No

4. **Set Environment Variables**
   ```bash
   fly secrets set DISCORD_BOT_TOKEN="your_token"
   fly secrets set SUPABASE_PROJECT_URL="your_url"
   fly secrets set SUPABASE_PUBLISHABLE_KEY="your_key"
   fly secrets set SUPABASE_SECRET_KEY="your_secret"
   fly secrets set GEMINI_API_KEY="your_key"
   fly secrets set MESSAGE_RETENTION_DAYS="30"
   fly secrets set CLEANUP_INTERVAL_HOURS="24"
   ```

5. **Deploy**
   ```bash
   fly deploy
   ```

---

## Option 4: Self-Hosting (VPS)

### Pros
- ✅ Full control
- ✅ No platform limitations
- ✅ Can be very cheap ($3-5/month)

### Cons
- ⚠️ Requires server management
- ⚠️ Need to handle updates/security

### Recommended Providers
- **DigitalOcean** - $4/month droplet
- **Linode** - $5/month
- **Vultr** - $2.50/month (limited availability)
- **Oracle Cloud** - Free tier (ARM instances)

### Setup Steps (Ubuntu/Debian)

1. **SSH into server**
   ```bash
   ssh root@your-server-ip
   ```

2. **Install Python**
   ```bash
   apt update
   apt install python3 python3-pip python3-venv git -y
   ```

3. **Clone repository**
   ```bash
   git clone https://github.com/yourusername/discord-ai-bot.git
   cd discord-ai-bot
   ```

4. **Setup environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Create .env file**
   ```bash
   nano .env
   # Paste your environment variables
   # Ctrl+X, Y, Enter to save
   ```

6. **Run with systemd (keeps bot running)**
   
   Create service file:
   ```bash
   nano /etc/systemd/system/discord-bot.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=Discord AI Bot
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/discord-ai-bot
   ExecStart=/root/discord-ai-bot/venv/bin/python main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

7. **Enable and start**
   ```bash
   systemctl daemon-reload
   systemctl enable discord-bot
   systemctl start discord-bot
   systemctl status discord-bot
   ```

8. **View logs**
   ```bash
   journalctl -u discord-bot -f
   ```

---

## Monitoring Your Bot

### Check if Bot is Running

**Render/Railway:**
- Check dashboard logs
- Look for "Bot logged in as..." message

**Fly.io:**
```bash
fly logs
```

**VPS:**
```bash
systemctl status discord-bot
journalctl -u discord-bot -f
```

### Discord Status

- Bot should show as "Online" in your server
- Test with `/ask query: test`

### Storage Monitoring

Check Supabase dashboard:
- Go to Table Editor → messages
- View row count
- Check database size in Settings

Bot logs will show storage stats after each cleanup:
```
[INFO] Current storage: 15000 total messages, 15000 from last 30 days
```

---

## Troubleshooting

### Bot Goes Offline

**Render Free Tier:**
- Check if you exceeded 750 hours/month
- Upgrade to paid tier ($7/month) for unlimited

**Railway:**
- Check if free credit ran out
- Add payment method

**Connection Issues:**
- Check environment variables are set correctly
- Verify Discord token is valid
- Check Supabase/Gemini API keys

### High Storage Usage

Adjust retention period:
```env
MESSAGE_RETENTION_DAYS=14  # Keep only 2 weeks
```

Or run manual cleanup more frequently:
```env
CLEANUP_INTERVAL_HOURS=12  # Cleanup every 12 hours
```

### Rate Limiting

If you hit Gemini rate limits:
- Free tier: 5 RPM for gemini-2.5-flash
- Consider upgrading to paid tier
- Or implement request queuing

---

## Cost Comparison

| Platform | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| **Render** | 750 hrs/month | $7/month unlimited | Small-medium bots |
| **Railway** | $5 credit/month | $5/month + usage | Testing/development |
| **Fly.io** | 3 shared VMs | ~$2/month | Production bots |
| **VPS** | None (Oracle free tier) | $3-5/month | Full control |

---

## Recommended Setup

**For most users:**
1. Start with **Render.com** free tier
2. Use 30-day message retention
3. Monitor storage in Supabase dashboard
4. Upgrade to paid ($7/month) if needed

**For high-traffic servers:**
1. Use **Fly.io** or **VPS**
2. Reduce retention to 14-21 days
3. Monitor logs for cleanup stats
4. Consider paid Gemini tier if hitting rate limits

---

## Next Steps After Deployment

1. ✅ Verify bot is online in Discord
2. ✅ Test all commands (`/ask`, `/recap`, `/settings`)
3. ✅ Monitor logs for first 24 hours
4. ✅ Check storage after first cleanup cycle
5. ✅ Adjust retention settings if needed

Your bot is now running 24/7 with automatic storage management! 🎉
