# TealDR Bot - Complete Technical Documentation

## 🤖 Overview

**TealDR** is an advanced Discord bot that provides semantic search, AI-powered Q&A, and episodic memory capabilities for Discord servers. It uses a hybrid Graph RAG (Retrieval-Augmented Generation) architecture combining vector embeddings, Neo4j knowledge graphs, and LLM-based query understanding.

---

## 🏗️ Architecture

### **Dual Database System**

1. **Supabase (PostgreSQL + pgvector)**
   - Stores raw message data with vector embeddings
   - Enables semantic search using cosine similarity
   - Handles time-based queries and filtering
   - Primary data store for all Discord messages

2. **Neo4j Graph Database**
   - Stores entities, relationships, and temporal connections
   - Enables complex graph traversal queries
   - Tracks entity evolution over time
   - Identifies experts and conversation threads

### **Tech Stack**

- **Language:** Python 3.11
- **Discord Library:** discord.py
- **Databases:** 
  - Supabase (PostgreSQL + pgvector extension)
  - Neo4j (Aura cloud instance)
- **AI/ML:**
  - Google Gemini 1.5 Flash (query understanding, response generation)
  - text-embedding-004 (vector embeddings)
- **Deployment:** Docker on GCP VM
- **Version Control:** GitHub

---

## 📊 Data Flow

### **Message Indexing Pipeline**

```
Discord Message
    ↓
1. Event Handler (bot/events.py)
    ↓
2. Check excluded channels
    ↓
3. Generate embedding (ai/embeddings.py)
    ↓
4. Store in Supabase (database/supabase_client.py)
    ↓
5. Extract entities (extraction/entity_extractor.py)
    ↓
6. Build graph (graph/builder.py)
    ↓
7. Store in Neo4j (db/neo4j.py)
```

### **Query Pipeline**

```
User Query (/ask, /lookup, /recap)
    ↓
1. Query Understanding (retrieval/query_engine.py)
   - Intent classification
   - Entity extraction
   - Time scope detection
    ↓
2. Retrieval Strategy Selection
   - Lookup: Semantic search entire database
   - Summarization: Recent messages by time
   - Expert Finding: Graph traversal
   - Relational: Entity relationship queries
    ↓
3. Vector Search (retrieval/vector_search.py)
   - Generate query embedding
   - Semantic search in Supabase
   - Filter by server_id, author, channel, time
    ↓
4. Graph Traversal (graph/queries.py)
   - Neo4j Cypher queries
   - Entity relationships
   - Temporal context
   - Conversation threads
    ↓
5. Response Generation (ai/gemini_client.py)
   - Combine vector + graph results
   - Generate natural language response
   - Apply server persona
    ↓
6. Format & Send (utils/embed_builder.py)
   - Discord embeds
   - Pagination for long responses
   - Reaction-based sources reveal
```

---

## 🎯 Core Features

### **1. Commands**

#### **/ask** - Natural Language Q&A
```
/ask query: what did @user talk about yesterday?
```
- AI-generated answers based on message history
- Supports follow-up questions with context
- Intent-based retrieval (lookup vs summarization)
- Sources hidden by default (reveal with 📊 reaction)
- Filters: channel, thread, date range, min_length, server_name

#### **/lookup** - Find Exact Messages
```
/lookup clues: deployment issues
```
- Shows raw message results (who said what, when, where)
- Semantic search across entire database
- Similarity threshold: ≥50% relevance
- Filters: author, channel, date range
- Timestamps in user's local timezone

#### **/recap** - Time-Based Summaries
```
/recap time: 3d user: @user channel: #general
```
- Summarizes messages from specific timeframe
- Filters by user, channel, or entire server
- Time formats: 1h, 30m, 2d, 1w
- Prioritizes recency over semantic relevance

#### **/settings** - Server Configuration (Admin Only)
```
/settings action: Exclude channel from indexing channel: #private
```
- Exclude/include channels from indexing
- View current settings
- Message retention settings
- Per-server configuration

#### **/customize** - Bot Persona (Admin Only)
```
/customize action: Set Persona persona: "You are a helpful coding assistant"
```
- Customize bot's response style per server
- View current persona
- Reset to default

#### **/clear** - Clear Conversation Context
```
/clear
```
- Clears user's conversation history with bot
- Resets follow-up question context

#### **/stats** - Server Statistics
```
/stats scope: server
```
- Server-wide message statistics
- Personal message statistics
- Activity metrics

#### **/export** - Export Search Results
```
/export query: API discussion format: json
```
- Export results to JSON, CSV, Markdown, or TXT
- Supports all search filters
- File download via Discord

#### **/timemachine** - Historical Lookback
```
/timemachine date: 03-15
```
- See what happened on this day in previous years
- Nostalgic server history feature

#### **/quiz** - Kahoot-Style Quiz
```
/quiz topic: server history difficulty: medium
```
- AI-generated quiz based on server messages
- Multiple choice questions
- Real-time scoring

#### **/trends** - Topic Trends
```
/trends topic: deployment timeframe: 30d
```
- Analyze topic discussion trends over time
- Frequency analysis
- Temporal patterns

#### **/help** - Command Help
```
/help
```
- Shows all available commands
- Usage examples
- Feature descriptions

---

### **2. Intent-Based Query Understanding**

The bot classifies queries into specific intents to optimize retrieval:

**Intent Types:**
- **lookup** - "who talked about X", "what did X say about Y"
- **summarization** - "what did I miss", "recent activity" (no specific entity)
- **expert_finding** - "who knows X", "who is expert in Y"
- **relational** - "how are X and Y related"
- **evolutionary** - "how did X evolve over time"
- **temporal_context** - "what happened with X over time"
- **conversation_threads** - "continue the discussion about X"

**Query Understanding Prompt:**
```json
{
  "intent": "lookup | relational | evolutionary | expert_finding | summarization | temporal_context | conversation_threads",
  "primary_entity": "main entity (lowercase)",
  "primary_entity_type": "person | topic | technology | null",
  "search_terms": ["keywords"],
  "temporal_context_needed": true/false,
  "time_scope": "recent | days | weeks | months | all_time"
}
```

---

### **3. Hybrid Graph RAG System**

#### **Vector Search (Supabase pgvector)**
- Semantic similarity using cosine distance
- Searches entire database or filtered subset
- Match threshold: 0.5 (50% similarity)
- Returns top-k results (configurable)

#### **Graph Traversal (Neo4j)**

**Node Types:**
- `Server` - Discord server
- `Channel` - Discord channel
- `Message` - Individual message
- `Author` - Message author
- `Entity` - Extracted entities (people, topics, technologies)
- `Chunk` - Message groupings for context

**Relationship Types:**
- `IN_SERVER` - Channel belongs to server
- `IN_CHANNEL` - Message in channel
- `AUTHORED` - Author wrote message
- `MENTIONS` - Message mentions entity
- `RELATES_TO` - Entity relationships
- `FOLLOWS` - Temporal message sequence
- `PART_OF` - Message part of chunk

**Cypher Queries:**

1. **LOOKUP_QUERY** - Find messages mentioning entity
```cypher
MATCH (s:Server {id: $server_id})<-[:IN_SERVER]-(c:Channel)<-[:IN_CHANNEL]-(m:Message)-[:MENTIONS]->(e:Entity)
WHERE toLower(e.name) CONTAINS toLower($entity_name)
RETURN m, e, c ORDER BY m.timestamp DESC LIMIT 20
```

2. **SUMMARIZATION_QUERY** - Recent server activity
```cypher
MATCH (s:Server {id: $server_id})<-[:IN_SERVER]-(c:Channel)<-[:IN_CHANNEL]-(m:Message)
WHERE m.timestamp >= $start_time AND m.timestamp <= $end_time
RETURN m, c ORDER BY m.timestamp DESC LIMIT 50
```

3. **EXPERT_FINDING_QUERY** - Find experts on topic
```cypher
MATCH (s:Server {id: $server_id})<-[:IN_SERVER]-(c:Channel)<-[:IN_CHANNEL]-(m:Message)-[:MENTIONS]->(e:Entity)
WHERE toLower(e.name) CONTAINS toLower($entity_name)
WITH m.author_id AS author_id, COUNT(m) AS mention_count
RETURN author_id, mention_count ORDER BY mention_count DESC LIMIT 10
```

4. **RELATIONAL_QUERY** - Entity relationships
```cypher
MATCH (s:Server {id: $server_id})<-[:IN_SERVER]-(c:Channel)<-[:IN_CHANNEL]-(m:Message)-[:MENTIONS]->(a:Entity)
MATCH (s)<-[:IN_SERVER]-(c2:Channel)<-[:IN_CHANNEL]-(m2:Message)-[:MENTIONS]->(b:Entity)
WHERE toLower(a.name) CONTAINS toLower($entity_a) AND toLower(b.name) CONTAINS toLower($entity_b)
RETURN m, m2, a, b
```

5. **TEMPORAL_CONTEXT_QUERY** - Cross-time discussions
```cypher
MATCH (s:Server {id: $server_id})<-[:IN_SERVER]-(c1:Channel)<-[:IN_CHANNEL]-(m1:Message)-[:MENTIONS]->(e:Entity)
OPTIONAL MATCH (s)<-[:IN_SERVER]-(c2:Channel)<-[:IN_CHANNEL]-(m2:Message)-[:MENTIONS]->(related_entity)
WHERE m2.timestamp > m1.timestamp
RETURN m1, m2, e, related_entity
```

6. **CONVERSATION_THREADS_QUERY** - Message sequences
```cypher
MATCH (s:Server {id: $server_id})<-[:IN_SERVER]-(c:Channel)<-[:IN_CHANNEL]-(m:Message)-[:MENTIONS]->(e:Entity)
MATCH (m)-[:FOLLOWS*1..3]->(next:Message)
RETURN m, next, e
```

---

### **4. Entity Extraction**

**Extraction Process:**
1. Group messages into time windows (5-minute chunks)
2. Send to Gemini for entity extraction
3. Extract: people, topics, technologies, events
4. Build relationships between entities
5. Store in Neo4j graph

**Entity Types:**
- **Person** - @mentions, usernames, real names
- **Topic** - Discussion subjects, themes
- **Technology** - Tools, frameworks, languages
- **Event** - Meetings, releases, incidents

**Relationship Strength:**
- Co-occurrence in same message: 1.0
- Co-occurrence in same chunk: 0.8
- Co-occurrence in same channel: 0.5

---

### **5. Server Isolation (Critical Security)**

**All queries filter by `server_id` to prevent cross-server data leaks:**

- Vector search: `server_id` filter in Supabase query
- Graph queries: `MATCH (s:Server {id: $server_id})` in all Cypher queries
- Message indexing: Stores `server_id` with every message
- Settings: Per-server excluded channels, persona, retention

**Files enforcing server isolation:**
- `retrieval/query_engine.py` - Passes `server_id` to all functions
- `retrieval/temporal_engine.py` - Filters by `server_id` in temporal queries
- `graph/queries.py` - All Cypher queries include server filtering
- `database/supabase_client.py` - Vector search filters by `server_id`

---

### **6. Conversation Context**

**Follow-up Question Support:**
- Tracks last query per user
- Maintains conversation context for 10 minutes
- Combines current query with previous context
- Allows natural follow-ups like "tell me more" or "what about X?"

**Implementation:**
```python
# utils/conversation_context.py
class ConversationContext:
    def __init__(self):
        self.contexts = {}  # user_id -> {query, timestamp}
    
    def add_context(self, user_id, query):
        self.contexts[user_id] = {
            'query': query,
            'timestamp': datetime.utcnow()
        }
    
    def get_context(self, user_id):
        # Returns context if < 10 minutes old
```

---

### **7. Sources Reveal Feature**

**Default Behavior:**
- `/ask` responses hide sources by default
- Clean, concise answers without clutter

**On-Demand Sources:**
- Bot adds 📊 reaction to responses
- User clicks 📊 to reveal sources
- Sources appear as temporary message (auto-delete after 60s)
- Shows: author, channel, date, message quote

**Implementation:**
```python
# bot/events.py
async def on_reaction_add(reaction, user):
    if str(reaction.emoji) == '📊':
        sources = response_data.get('sources')
        await channel.send(f"📊 Sources: {sources}", delete_after=60)
```

---

### **8. Excluded Channels**

**Admin Configuration:**
- `/settings action: Exclude channel from indexing channel: #private`
- Messages from excluded channels are NOT indexed
- Applies to real-time indexing and backfill

**Enforcement:**
```python
# bot/events.py on_message
excluded_channels = await server_settings_client.get_excluded_channels(server_id)
if message.channel.id in excluded_channels:
    return  # Skip indexing
```

---

### **9. Background Jobs**

**Cleanup Task:**
- Runs every 24 hours (configurable)
- Deletes messages older than retention period (default: 30 days)
- Maintains database size
- Logs storage statistics

**Backfill on Server Join:**
- Auto-indexes past 5 days of messages when bot joins new server
- Respects excluded channels
- Rate-limited to avoid API throttling
- Runs in background (non-blocking)

---

## 📁 Project Structure

```
tealdr-backend/
├── ai/
│   ├── embeddings.py          # Text embedding generation
│   └── gemini_client.py       # Gemini API client
├── bot/
│   ├── commands.py            # All Discord commands
│   └── events.py              # Event handlers (on_message, on_reaction_add)
├── database/
│   ├── supabase_client.py     # Supabase operations
│   ├── queries.py             # SQL queries
│   ├── server_settings.py     # Server configuration
│   └── feedback_client.py     # User feedback storage
├── db/
│   └── neo4j.py               # Neo4j driver initialization
├── extraction/
│   └── entity_extractor.py    # Entity extraction from messages
├── graph/
│   ├── builder.py             # Build Neo4j graph from extractions
│   ├── queries.py             # Cypher query definitions
│   └── schema.py              # Neo4j schema setup
├── ingestion/
│   └── chunker.py             # Message chunking for entity extraction
├── retrieval/
│   ├── query_engine.py        # Main query pipeline
│   ├── temporal_engine.py     # Temporal query handling
│   └── vector_search.py       # Vector search logic
├── utils/
│   ├── embed_builder.py       # Discord embed formatting
│   ├── helpers.py             # Time parsing, utilities
│   ├── logger.py              # Logging configuration
│   ├── conversation_context.py # Follow-up question context
│   ├── cleanup.py             # Message cleanup jobs
│   └── server_selector.py     # Multi-server selection
├── config.py                  # Environment configuration
├── main.py                    # Bot entry point
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker container config
└── .env                       # Environment variables
```

---

## 🔧 Configuration

### **Environment Variables (.env)**

```bash
# Discord
DISCORD_BOT_TOKEN=your_bot_token

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key

# Neo4j
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Google AI
GEMINI_API_KEY=your_gemini_api_key

# Features
GRAPH_RAG_ENABLED=true
VECTOR_TOP_K=20
CLEANUP_INTERVAL_HOURS=24
MESSAGE_RETENTION_DAYS=30
```

### **Key Configuration Values**

```python
# config.py
class Config:
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GRAPH_RAG_ENABLED = os.getenv("GRAPH_RAG_ENABLED", "true").lower() == "true"
    VECTOR_TOP_K = int(os.getenv("VECTOR_TOP_K", "20"))
    CLEANUP_INTERVAL_HOURS = int(os.getenv("CLEANUP_INTERVAL_HOURS", "24"))
    MESSAGE_RETENTION_DAYS = int(os.getenv("MESSAGE_RETENTION_DAYS", "30"))
```

---

## 🚀 Deployment

### **Docker Deployment**

```bash
# Build image
docker build -t tealdr-bot .

# Run container
docker run -d \
  --name tealdr-bot \
  --env-file .env \
  --restart unless-stopped \
  tealdr-bot
```

### **GCP VM Deployment**

```bash
# Update script (update-vm.ps1)
1. Push code to GitHub
2. SSH to GCP VM
3. Pull latest code
4. Stop current container
5. Rebuild Docker image
6. Start new container
7. Show logs
```

### **Deployment Checklist**

- [ ] Environment variables configured in `.env`
- [ ] Supabase database schema created
- [ ] Neo4j database initialized with schema
- [ ] Discord bot token valid
- [ ] Gemini API key valid
- [ ] Docker image builds successfully
- [ ] Bot connects to Discord
- [ ] Commands sync successfully

---

## 🗄️ Database Schemas

### **Supabase (PostgreSQL)**

```sql
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    message_id BIGINT UNIQUE NOT NULL,
    server_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    channel_name TEXT,
    thread_id BIGINT,
    is_thread_message BOOLEAN DEFAULT FALSE,
    author_id BIGINT NOT NULL,
    author_name TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    embedding vector(768),  -- pgvector extension
    indexed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_server_id ON messages(server_id);
CREATE INDEX idx_messages_channel_id ON messages(channel_id);
CREATE INDEX idx_messages_author_id ON messages(author_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_embedding ON messages USING ivfflat (embedding vector_cosine_ops);

-- Semantic search function
CREATE OR REPLACE FUNCTION match_messages(
    query_embedding vector(768),
    match_threshold float,
    match_count int,
    server_id_filter bigint
)
RETURNS TABLE (
    id bigint,
    message_id bigint,
    server_id bigint,
    channel_id bigint,
    author_id bigint,
    author_name text,
    content text,
    created_at timestamptz,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.message_id,
        m.server_id,
        m.channel_id,
        m.author_id,
        m.author_name,
        m.content,
        m.created_at,
        1 - (m.embedding <=> query_embedding) AS similarity
    FROM messages m
    WHERE m.server_id = server_id_filter
        AND 1 - (m.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;
```

### **Neo4j Graph Schema**

```cypher
// Constraints
CREATE CONSTRAINT message_id IF NOT EXISTS FOR (m:Message) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT author_id IF NOT EXISTS FOR (a:Author) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT server_id IF NOT EXISTS FOR (s:Server) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT channel_id IF NOT EXISTS FOR (c:Channel) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (ch:Chunk) REQUIRE ch.id IS UNIQUE;

// Indexes
CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name);
CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type);
CREATE INDEX message_timestamp IF NOT EXISTS FOR (m:Message) ON (m.timestamp);
CREATE INDEX chunk_start_time IF NOT EXISTS FOR (ch:Chunk) ON (ch.start_time);
CREATE INDEX chunk_channel IF NOT EXISTS FOR (ch:Chunk) ON (ch.channel_id);
```

---

## 🔍 Key Algorithms

### **Cosine Similarity (Vector Search)**

```python
def _cosine_similarity(self, vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    return dot_product / (magnitude1 * magnitude2)
```

### **Time Range Parsing**

```python
def parse_time_range(time_str):
    """Parse time strings like '3d', '2h', '30m' into datetime range."""
    now = datetime.utcnow()
    
    if time_str.endswith('h'):
        hours = int(time_str[:-1])
        start_time = now - timedelta(hours=hours)
    elif time_str.endswith('m'):
        minutes = int(time_str[:-1])
        start_time = now - timedelta(minutes=minutes)
    elif time_str.endswith('d'):
        days = int(time_str[:-1])
        start_time = now - timedelta(days=days)
    elif time_str.endswith('w'):
        weeks = int(time_str[:-1])
        start_time = now - timedelta(weeks=weeks)
    
    return (start_time, now)
```

### **Message Chunking**

```python
def group_messages_into_windows(messages, window_minutes=5):
    """Group messages into time windows for entity extraction."""
    chunks = []
    current_chunk = []
    current_start = None
    
    for msg in sorted(messages, key=lambda x: x['created_at']):
        msg_time = msg['created_at']
        
        if current_start is None:
            current_start = msg_time
            current_chunk.append(msg)
        elif (msg_time - current_start).total_seconds() / 60 <= window_minutes:
            current_chunk.append(msg)
        else:
            chunks.append(current_chunk)
            current_chunk = [msg]
            current_start = msg_time
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks
```

---

## 🐛 Known Issues & Fixes

### **Issue 1: Cross-Server Data Leak (FIXED)**
- **Problem:** Queries returned data from other servers
- **Root Cause:** Neo4j queries didn't filter by `server_id`
- **Fix:** Added `server_id` filtering to all Cypher queries
- **Files:** `graph/queries.py`, `retrieval/query_engine.py`, `retrieval/temporal_engine.py`

### **Issue 2: Irrelevant Search Results (FIXED)**
- **Problem:** `/lookup` returned unrelated messages
- **Root Cause:** Used `semantic_search_filtered()` which only searched 200 recent messages
- **Fix:** Switched to `semantic_search()` with pgvector across entire database
- **Files:** `bot/commands.py`

### **Issue 3: Wrong Timezone in Timestamps (FIXED)**
- **Problem:** Timestamps showed UTC instead of user's local time
- **Root Cause:** Static timestamp formatting
- **Fix:** Use Discord's `<t:unix:f>` format for auto timezone conversion
- **Files:** `bot/commands.py`

---

## 📈 Performance Considerations

### **Vector Search Optimization**
- pgvector IVFFlat index for fast similarity search
- Limit results to top-k (default: 20)
- Filter by server_id before similarity calculation
- Cache embeddings in database

### **Graph Query Optimization**
- Indexes on frequently queried properties
- Limit graph traversal depth
- Use UNION for multiple query patterns
- Server_id filtering at query start

### **Rate Limiting**
- 5 requests per minute per user
- Prevents API abuse
- Configurable limits

### **Message Cleanup**
- Automatic deletion of old messages
- Configurable retention period
- Runs during low-traffic hours
- Maintains database performance

---

## 🔐 Security Features

1. **Server Isolation** - Complete data separation between Discord servers
2. **Admin-Only Commands** - Settings and customization require admin role
3. **Excluded Channels** - Admins can exclude sensitive channels from indexing
4. **Rate Limiting** - Prevents spam and API abuse
5. **Environment Variables** - Secrets stored securely, not in code
6. **Docker Isolation** - Bot runs in isolated container
7. **Non-Root User** - Docker container runs as non-root user

---

## 🎨 UI/UX Features

1. **Discord Embeds** - Rich, formatted responses
2. **Pagination** - Long responses split into pages with navigation
3. **Reactions** - 👍 👎 for feedback, 📊 to reveal sources
4. **Ephemeral Messages** - Settings responses only visible to user
5. **Thinking Indicator** - Shows bot is processing query
6. **Auto-Delete** - Temporary messages auto-delete after timeout
7. **Local Timestamps** - Automatic timezone conversion
8. **Color Coding** - Blue for search, green for recap, red for errors

---

## 📚 Dependencies

```txt
discord.py==2.3.2
supabase==2.0.3
neo4j==5.14.0
google-generativeai==0.3.1
python-dotenv==1.0.0
asyncio
aiohttp
```

---

## 🔄 Recent Updates

### **March 2026**
- ✅ Fixed cross-server data leak (server isolation)
- ✅ Added `/lookup` command for exact message search
- ✅ Implemented sources reveal with 📊 reaction
- ✅ Fixed timestamp timezone display
- ✅ Improved semantic search relevance
- ✅ Added similarity threshold filtering

### **February 2026**
- ✅ Implemented hybrid Graph RAG architecture
- ✅ Added entity extraction and graph building
- ✅ Created temporal query pipeline
- ✅ Added conversation context for follow-ups
- ✅ Implemented excluded channels feature

---

## 🎯 Future Roadmap

### **Planned Features**
- Voice channel transcription (Whisper API)
- Multi-server search improvements
- Advanced analytics dashboard
- Webhook integrations (Slack, GitHub, Jira)
- Custom entity types
- Relationship strength learning
- Query performance analytics
- A/B testing for retrieval strategies

---

## 📞 Support & Maintenance

### **Logs**
```bash
# View bot logs
sudo docker logs -f tealdr-bot

# View last 100 lines
sudo docker logs --tail 100 tealdr-bot
```

### **Restart Bot**
```bash
sudo docker restart tealdr-bot
```

### **Update Bot**
```powershell
# From local machine
.\update-vm.ps1
```

### **Database Maintenance**
```sql
-- Supabase: Check message count
SELECT COUNT(*) FROM messages;

-- Supabase: Check storage size
SELECT pg_size_pretty(pg_total_relation_size('messages'));

-- Neo4j: Check node count
MATCH (n) RETURN count(n);

-- Neo4j: Check relationship count
MATCH ()-[r]->() RETURN count(r);
```

---

## 🧪 Testing

### **Manual Testing Checklist**
- [ ] `/ask` returns relevant results
- [ ] `/lookup` finds exact messages
- [ ] `/recap` summarizes timeframe
- [ ] Sources reveal with 📊 works
- [ ] Timestamps show in local timezone
- [ ] Server isolation enforced
- [ ] Excluded channels respected
- [ ] Follow-up questions work
- [ ] Rate limiting prevents spam
- [ ] Pagination works for long responses

### **Test Queries**
```
/ask query: what did @user talk about?
/lookup clues: deployment issues
/recap time: 3d
/settings action: View current settings
/stats scope: server
```

---

## 💡 Best Practices

### **For Users**
- Be specific in queries for better results
- Use `/lookup` for exact quotes, `/ask` for summaries
- Exclude sensitive channels from indexing
- Provide feedback with 👍 👎 reactions
- Use date filters to narrow results

### **For Developers**
- Always filter by `server_id` in queries
- Use async/await for database operations
- Log errors with context
- Handle edge cases (empty results, API failures)
- Test with multiple servers
- Document new features
- Follow existing code patterns

---

## 📖 Additional Resources

- **Discord.py Docs:** https://discordpy.readthedocs.io/
- **Supabase Docs:** https://supabase.com/docs
- **Neo4j Docs:** https://neo4j.com/docs/
- **Gemini API Docs:** https://ai.google.dev/docs
- **pgvector Docs:** https://github.com/pgvector/pgvector

---

## 📝 License & Credits

**Developer:** limo.ew  
**Contributors:** sidtheitguy, quantadude, papitaa_partyy  
**License:** Private/Proprietary  
**Version:** 1.0.0  
**Last Updated:** March 2026

---

**End of Documentation**
