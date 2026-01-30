# Discord AI Search Bot

A Discord bot that enables natural language search and AI-powered queries across server message history using Google Gemini and Supabase.

## Features

- 🔍 **Natural Language Search**: Ask questions like "what did @user talk about yesterday?"
- 📊 **Smart Recaps**: Get AI-generated summaries of conversations over time
- 🎯 **Semantic Search**: Uses embeddings for intelligent message retrieval
- ⚙️ **Admin Controls**: Exclude channels from indexing
- 🚀 **Real-time Indexing**: Automatically indexes new messages as they're sent

## Prerequisites

- Python 3.11 or higher
- Discord Bot Token
- Supabase Account (free tier works)
- Google Gemini API Key (free tier works)

## Installation

### 1. Clone and Setup

```bash
cd c:\bot
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 2. Get API Keys

#### Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to "Bot" section and click "Add Bot"
4. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent
   - Presence Intent
5. Copy the bot token

#### Supabase Setup
1. Create account at [Supabase](https://supabase.com)
2. Create a new project
3. Go to Project Settings → API
4. Copy the Project URL, Publishable Key (anon), and Secret Key (service_role)
5. Go to SQL Editor and run the schema from `database/schema.sql`:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id BIGINT UNIQUE NOT NULL,
    server_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    author_name TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX idx_server_channel ON messages(server_id, channel_id);
CREATE INDEX idx_author_id ON messages(author_id);
CREATE INDEX idx_created_at ON messages(created_at);
CREATE INDEX idx_message_id ON messages(message_id);

-- Create index for vector similarity search
CREATE INDEX ON messages USING ivfflat (embedding vector_cosine_ops);
```

#### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the API key

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
DISCORD_BOT_TOKEN=your_actual_discord_bot_token
SUPABASE_PROJECT_URL=your_actual_supabase_project_url
SUPABASE_PUBLISHABLE_KEY=your_actual_supabase_publishable_key
SUPABASE_SECRET_KEY=your_actual_supabase_secret_key
GEMINI_API_KEY=your_actual_gemini_api_key
EXCLUDED_CHANNELS=
LOG_LEVEL=INFO
```

### 4. Invite Bot to Server

1. Go to Discord Developer Portal → Your Application → OAuth2 → URL Generator
2. Select scopes: `bot`, `applications.commands`
3. Select bot permissions:
   - Read Messages/View Channels
   - Send Messages
   - Read Message History
   - Use Slash Commands
4. Copy the generated URL and open it in your browser
5. Select your server and authorize

### 5. Run the Bot

```bash
python main.py
```

You should see:
```
[2024-01-30 17:00:00] [INFO] root: Configuration validated successfully
[2024-01-30 17:00:00] [INFO] root: Starting Discord bot...
[2024-01-30 17:00:01] [INFO] bot.events: Bot logged in as YourBot (ID: 123456789)
[2024-01-30 17:00:01] [INFO] bot.events: Connected to 1 servers
[2024-01-30 17:00:01] [INFO] bot.events: Synced 3 command(s)
```

## Usage

### `/ask` Command

Ask natural language questions about server messages.

**Examples:**
```
/ask query: what did @Roop talk about yesterday?
/ask query: show me travel posts from @limo
/ask query: what did I miss this week?
/ask query: summarize the discussion about the project
```

**Features:**
- Automatically detects user mentions
- Understands time ranges (yesterday, today, this week, last week)
- Uses AI to generate contextual answers

### `/recap` Command

Get AI-generated summaries of conversations.

**Examples:**
```
/recap time: Last 24 hours
/recap time: Last 7 days user: @Roop
/recap time: Last 30 days channel: #general
```

**Parameters:**
- `time` (required): Choose from 24h, 7d, or 30d
- `user` (optional): Filter by specific user
- `channel` (optional): Filter by specific channel

### `/settings` Command (Admin Only)

Manage bot configuration.

**Examples:**
```
/settings action: View current settings
/settings action: Exclude channel from indexing channel: #private
/settings action: Include channel for indexing channel: #general
```

## How It Works

1. **Message Indexing**: Bot listens to all messages in channels it has access to
2. **Embedding Generation**: Each message is converted to a 768-dimensional vector using Gemini
3. **Storage**: Messages and embeddings are stored in Supabase with pgvector
4. **Search**: When you ask a question:
   - Your query is converted to an embedding
   - Similar messages are found using vector similarity search
   - Results are filtered by user/time if specified
   - AI generates a natural language response

## Project Structure

```
discord-ai-bot/
├── .env                    # Your API keys (create from .env.example)
├── .env.example           # Template for environment variables
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── config.py             # Configuration management
├── main.py               # Entry point
├── bot/
│   ├── commands.py       # Slash command handlers
│   ├── events.py         # Event listeners
│   └── permissions.py    # Permission checks
├── database/
│   ├── supabase_client.py   # Supabase connection
│   ├── queries.py           # Database query functions
│   └── schema.sql           # Database schema
├── ai/
│   ├── gemini_client.py     # Gemini API wrapper
│   ├── embeddings.py        # Embedding generation
│   └── prompts.py           # Prompt templates
└── utils/
    ├── logger.py            # Logging configuration
    └── helpers.py           # Utility functions
```

## Troubleshooting

### Bot doesn't respond to commands
- Make sure slash commands are synced (check bot logs)
- Verify bot has proper permissions in your server
- Try kicking and re-inviting the bot

### "Missing required environment variables" error
- Check your `.env` file exists and has all required variables
- Make sure there are no extra spaces in your `.env` file
- Verify API keys are correct

### Messages not being indexed
- Check bot has "Read Messages" permission in channels
- Verify channel is not in excluded list
- Check bot logs for errors

### Supabase connection errors
- Verify your Supabase URL and key are correct
- Make sure you ran the schema.sql in Supabase SQL Editor
- Check that pgvector extension is enabled

### Gemini API errors
- Verify your API key is valid
- Check you haven't exceeded free tier limits
- Try regenerating your API key

## Rate Limits

- Users are limited to 10 queries per minute
- Gemini free tier: 60 requests per minute
- Supabase free tier: Unlimited requests, 500MB database

## Privacy & Data

- Bot only indexes messages in channels where it's invited
- Messages are stored with content, author info, and timestamps
- Embeddings are mathematical representations, not readable text
- Use `/settings` to exclude sensitive channels
- All data is stored in your Supabase instance (you control it)

## Future Enhancements

- [ ] Backfill historical messages
- [ ] Web dashboard for analytics
- [ ] Daily/weekly automated recaps
- [ ] Export functionality (PDF summaries)
- [ ] Multi-server search
- [ ] Voice channel transcription

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review bot logs in `bot.log`
3. Verify all API keys are correct
4. Check Supabase and Gemini service status

## License

MIT License - Feel free to modify and use for your own projects!
