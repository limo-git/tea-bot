# TeaL;DR RAG Pipeline Architecture

Complete end-to-end Retrieval-Augmented Generation pipeline documentation.

---

## 🔄 Complete Pipeline Flow

```
INGESTION → RETRIEVAL → GENERATION
```

---

## 📥 INGESTION PIPELINE

**Goal:** Parse → Chunk → Contextualize → Embed → Store

### 1. **Parse** (`bot/events.py`)
- **Location:** `on_message` event handler
- **Process:** Discord messages captured in real-time
- **Output:** Raw message data (content, author, channel, timestamp, attachments)

```python
# bot/events.py - on_message()
- Captures Discord messages
- Filters out bot messages
- Checks private sessions
- Extracts metadata (author, channel, timestamp)
```

### 2. **Chunk** (`ingestion/chunker.py`)
- **Location:** `jobs/chunker_job.py` (runs every 5 minutes)
- **Process:** 
  - Fetches recent messages (last 5 minutes)
  - Groups messages by conversation context
  - Creates semantic chunks with overlap
  - Adds metadata (server_id, channel_id, timestamps)
- **Output:** Message chunks ready for embedding

```python
# ingestion/chunker.py
- chunk_messages_by_conversation()
  - Groups messages by time proximity
  - Maintains conversation context
  - Adds chunk metadata
```

### 3. **Contextualize** (`extraction/entity_extractor.py` + `graph/builder.py`)
- **Location:** Graph building process
- **Process:**
  - Extract entities (people, topics, technologies)
  - Build relationships between entities
  - Add temporal context
  - Create conversation threads
- **Output:** Contextualized entities and relationships

```python
# extraction/entity_extractor.py
- extract_entities_from_message()
  - Uses Gemini to extract entities
  - Identifies entity types (person, topic, technology)
  - Extracts relationships

# graph/builder.py
- build_graph_from_messages()
  - Creates Neo4j nodes and relationships
  - Adds temporal decay weights
  - Builds conversation threads
```

### 4. **Embed** (`ai/embeddings.py`)
- **Location:** Embedding generation for messages
- **Process:**
  - Generate embeddings using text-embedding-004
  - 768-dimensional vectors
  - Batch processing for efficiency
- **Output:** Vector embeddings

```python
# ai/embeddings.py
- generate_embeddings()
  - Uses Google's text-embedding-004
  - Generates 768-dim vectors
  - Handles batch processing
```

### 5. **Store** (`database/supabase_client.py` + `db/neo4j.py`)
- **Location:** Dual storage (Supabase + Neo4j)
- **Process:**
  - **Supabase:** Store messages + embeddings (pgvector)
  - **Neo4j:** Store knowledge graph (entities + relationships)
- **Output:** Indexed and searchable data

```python
# database/supabase_client.py
- store_message()
  - Stores message content
  - Stores embedding vector
  - Indexes for semantic search

# db/neo4j.py + graph/builder.py
- create_or_update_entity()
- create_relationship()
  - Stores entities and relationships
  - Adds temporal metadata
```

---

## 🔍 RETRIEVAL PIPELINE

**Goal:** Question → Transform → Hybrid Search → Rerank → Compress

### 1. **Question Transform** (`retrieval/query_engine.py`)
- **Location:** `understand_query()` function
- **Process:**
  - Parse user query with Gemini
  - Extract intent (lookup, expert_finding, summarization, etc.)
  - Identify entities and search terms
  - Determine temporal scope
- **Output:** Structured query understanding

```python
# retrieval/query_engine.py - understand_query()
- Uses Gemini to parse query
- Extracts:
  - intent (lookup, relational, expert_finding, etc.)
  - primary_entity
  - search_terms
  - temporal_context_needed
  - time_scope
```

### 2. **Hybrid Search** (`retrieval/vector_search.py` + `graph/queries.py`)
- **Location:** Parallel graph + vector search
- **Process:**
  - **BM25 Keyword Search:** Exact keyword matching (via Supabase full-text)
  - **Dense Vector Search:** Semantic similarity (pgvector cosine similarity)
  - **Graph Traversal:** Cypher queries for relationships (Neo4j)
  - **Reciprocal Rank Fusion (RRF):** Combine results
- **Output:** Ranked candidate documents

```python
# retrieval/vector_search.py
- vector_search()
  - Generates query embedding
  - Semantic search via pgvector
  - Applies confidence threshold (0.35)
  - Filters by author, channel, time

# graph/queries.py
- run_intent_query()
  - ENTITY_SEARCH_QUERY (lookup)
  - EXPERT_FINDING_QUERY (who knows X)
  - RELATIONAL_QUERY (how X relates to Y)
  - EVOLUTIONARY_QUERY (how X changed over time)
```

### 3. **Rerank** (`retrieval/context_assembler.py`)
- **Location:** `assemble_context()` function
- **Process:**
  - Deduplicate results
  - Prioritize by source (graph vs vector)
  - Apply recency bias for time-sensitive queries
  - Score by relevance + confidence
- **Output:** Reranked results

```python
# retrieval/context_assembler.py - assemble_context()
- Deduplicates by message_id
- Prioritizes graph results (structural relevance)
- Adds vector results (semantic relevance)
- Sorts by combined score
```

### 4. **Compress** (`retrieval/crag_refiner.py`)
- **Location:** CRAG (Corrective RAG) refinement
- **Process:**
  - Evaluate retrieval quality
  - If low confidence: refine query and re-retrieve
  - Filter out low-relevance chunks
  - Keep only high-confidence results
- **Output:** Compressed, high-quality context

```python
# retrieval/crag_refiner.py - refine_and_retrieve()
- Checks confidence scores
- Generates refined queries if needed
- Re-retrieves with better query
- Filters low-confidence results
```

---

## 🎯 GENERATION PIPELINE

**Goal:** Prompt → LLM → Answer with Citations

### 1. **Prompt** (`generation/answer_generator.py`)
- **Location:** `ANSWER_PROMPT` template
- **Process:**
  - Separate system instructions from context
  - Inject structured metadata with each document
  - Add explicit grounding rules
  - Specify citation format
  - Handle empty retrieval case
- **Output:** Structured prompt with context

```python
# generation/answer_generator.py - ANSWER_PROMPT
<system_instructions>
  - Explicit grounding rules
  - Uncertainty handling
  - Citation format
  - No fabrication rules
</system_instructions>

<retrieved_context>
  [Doc 1 | timestamp | source | author | channel]
  Message content...
  ---
  [Doc 2 | timestamp | source | author | channel]
  Message content...
</retrieved_context>

<task>
  Question: {query}
  Answer using ONLY the context above.
</task>
```

### 2. **LLM** (`generation/answer_generator.py`)
- **Location:** `generate_answer()` function
- **Process:**
  - Use Gemini 2.5 Flash
  - Temperature: 0.3 (low for factual accuracy)
  - Max tokens: 8192
  - Retry logic (3 attempts)
- **Output:** Generated answer

```python
# generation/answer_generator.py - generate_answer()
- Calls Gemini 2.5 Flash
- Temperature: 0.3
- Max output: 8192 tokens
- Tenacity retry (3 attempts)
```

### 3. **Answer with Citations** (`generation/answer_generator.py`)
- **Location:** LLM output with inline citations
- **Process:**
  - LLM generates answer grounded in context
  - Inline citations: [Author in #channel]
  - Distinguishes "shows" vs "suggests" vs "not covered"
  - Provides suggestions if no answer found
- **Output:** Final answer with citations

```python
# Expected output format:
"According to limo.ew in #general, the deployment was successful.
The messages suggest the API endpoint was fixed on April 5th."
```

---

## 📊 Pipeline Components Summary

### **INGESTION**
| Step | Component | Location | Output |
|------|-----------|----------|--------|
| Parse | Discord events | `bot/events.py` | Raw messages |
| Chunk | Message chunker | `ingestion/chunker.py` | Conversation chunks |
| Contextualize | Entity extraction + Graph | `extraction/entity_extractor.py`, `graph/builder.py` | Entities + relationships |
| Embed | Embedding generation | `ai/embeddings.py` | 768-dim vectors |
| Store | Dual storage | `database/supabase_client.py`, `db/neo4j.py` | Indexed data |

### **RETRIEVAL**
| Step | Component | Location | Output |
|------|-----------|----------|--------|
| Question Transform | Query understanding | `retrieval/query_engine.py` | Structured query |
| Hybrid Search | Vector + Graph + BM25 | `retrieval/vector_search.py`, `graph/queries.py` | Candidate docs |
| Rerank | Context assembly | `retrieval/context_assembler.py` | Ranked results |
| Compress | CRAG refinement | `retrieval/crag_refiner.py` | High-quality context |

### **GENERATION**
| Step | Component | Location | Output |
|------|-----------|----------|--------|
| Prompt | Structured prompt | `generation/answer_generator.py` | Formatted prompt |
| LLM | Gemini 2.5 Flash | `generation/answer_generator.py` | Raw answer |
| Citations | Inline attribution | `generation/answer_generator.py` | Final answer |

---

## 🔧 Key Features

### **Ingestion**
- ✅ Real-time message capture
- ✅ Semantic chunking with context
- ✅ Entity extraction (people, topics, tech)
- ✅ Knowledge graph building
- ✅ Vector embeddings (768-dim)
- ✅ Dual storage (Supabase + Neo4j)

### **Retrieval**
- ✅ Query understanding with LLM
- ✅ 7 different retrieval pipelines by intent
- ✅ Hybrid search (BM25 + dense vectors + graph)
- ✅ Reciprocal Rank Fusion (RRF)
- ✅ Confidence gating (threshold: 0.35)
- ✅ CRAG loop for query refinement
- ✅ Context compression

### **Generation**
- ✅ Strict RAG grounding rules
- ✅ Explicit uncertainty handling
- ✅ Structured context with metadata
- ✅ Inline citations [Author in #channel]
- ✅ No hallucinations (confidence gating)
- ✅ Empty retrieval handling
- ✅ Synthesized answers (not verbatim quotes)

---

## 🧪 Testing

### **Pipeline Tests**
- `tests/comprehensive_rag_test.py` - End-to-end pipeline tests
- `tests/test_rag_prompt_rules.py` - Generation prompt validation
- `tests/test_confidence_threshold.py` - Retrieval quality tests
- `tests/test_crag_refinement.py` - CRAG loop validation

### **Run Tests**
```powershell
# Complete pipeline tests
.\run_comprehensive_tests.ps1

# RAG prompt rules tests
.\run_rag_tests.ps1
```

---

## 📈 Performance Metrics

- **Ingestion:** ~5 min batch processing
- **Retrieval:** <2 seconds average
- **Generation:** 2-5 seconds (LLM call)
- **Total latency:** 3-7 seconds end-to-end
- **Confidence threshold:** 0.35 (filters weak results)
- **Context window:** Up to 10 documents
- **Storage:** 30-day retention (auto-cleanup)

---

## 🚀 Future Enhancements

### **Ingestion**
- [ ] Multi-modal support (images, files)
- [ ] Advanced chunking strategies
- [ ] Cross-server entity linking

### **Retrieval**
- [ ] Query expansion
- [ ] Learned reranking model
- [ ] Adaptive confidence thresholds
- [ ] Multi-hop reasoning

### **Generation**
- [ ] Streaming responses
- [ ] Multi-turn conversations
- [ ] Source document links
- [ ] Confidence scores in output
