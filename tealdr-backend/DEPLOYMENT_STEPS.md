# Deploy New RAG Pipeline to Production

## 🚀 Quick Deployment Steps

### 1. Pull Latest Code on Server
```bash
cd ~/tea-bot
git pull origin main
```

### 2. Rebuild Docker Container
```bash
cd ~/tea-bot/tealdr-backend
sudo docker-compose down
sudo docker-compose build --no-cache
sudo docker-compose up -d
```

### 3. Verify Deployment
```bash
# Check logs for new pipeline components
sudo docker logs -f tealdr-bot | grep -E "Hybrid search|RRF fusion|Reranking|Compression"
```

### 4. Test Query
Run in Discord:
```
/ask who talked about Python
```

### 5. Expected Log Output
```
[INFO] retrieval.query_engine: Hybrid search query: 'python python'
[INFO] retrieval.hybrid_search: Hybrid search with graph: query='python', X graph results
[INFO] retrieval.rrf_fusion: RRF fusion: X BM25, X vector, X graph results
[INFO] retrieval.rrf_fusion: RRF fusion complete: X unique documents
[INFO] retrieval.reranker: Reranking X results for query: 'python'
[INFO] retrieval.compressor: Compressing to budget: 4000 tokens
[INFO] retrieval.query_engine: Hybrid search returned X fused results
[INFO] retrieval.query_engine: Reranking complete: X results
[INFO] retrieval.query_engine: Compression complete: X results within token budget
```

---

## 🐛 Current Issue

The Docker container is running **old code** that doesn't have:
- Hybrid search
- RRF fusion
- Reranking
- Compression

**Symptoms:**
- Logs show `Vector search query` instead of `Hybrid search query`
- No RRF fusion logs
- No reranking logs
- Confidence threshold filtering out all results

---

## 🔍 Additional Fixes Needed

### 1. Fix Confidence Threshold (Too Aggressive)

**File:** `retrieval/vector_search.py`

The 0.35 threshold is filtering out ALL results. Lower it temporarily:

```python
# Line ~70
CONFIDENCE_THRESHOLD = 0.25  # Lower from 0.35
```

### 2. Fix Duplicate Query Terms

**File:** `retrieval/query_engine.py` line 391

Change:
```python
search_query = f"{understanding['primary_entity']} {' '.join(understanding.get('search_terms', []))}"
```

To:
```python
# Avoid duplicating entity if it's already in search terms
entity = understanding.get('primary_entity', '')
search_terms = understanding.get('search_terms', [])
if entity and entity not in ' '.join(search_terms):
    search_query = f"{entity} {' '.join(search_terms)}"
else:
    search_query = ' '.join(search_terms) if search_terms else entity
```

### 3. Fix Graph Traversal Syntax Error

**File:** `graph/queries.py`

The Neo4j query has a syntax error. Need to fix the DISTINCT aggregation issue.

---

## 📋 Deployment Checklist

- [ ] Pull latest code: `git pull origin main`
- [ ] Rebuild container: `sudo docker-compose build --no-cache`
- [ ] Restart container: `sudo docker-compose up -d`
- [ ] Check logs: `sudo docker logs -f tealdr-bot`
- [ ] Test query: `/ask who talked about Python`
- [ ] Verify hybrid search logs appear
- [ ] Verify RRF fusion logs appear
- [ ] Verify reranking logs appear
- [ ] Verify results are returned (not filtered out)

---

## 🎯 Quick Fix Commands

Run these on your server:

```bash
# Navigate to project
cd ~/tea-bot

# Pull latest code
git pull origin main

# Rebuild and restart
cd tealdr-backend
sudo docker-compose down
sudo docker-compose build --no-cache
sudo docker-compose up -d

# Watch logs
sudo docker logs -f tealdr-bot
```

Then test with: `/ask who talked about Python`
