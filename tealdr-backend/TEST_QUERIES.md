# TeaL;DR Bot - Test Queries

Comprehensive test queries to validate the complete RAG pipeline in production.

---

## 🎯 **1. LOOKUP INTENT** (Specific Topic Queries)

These should use **hybrid search (BM25 + Vector + Graph)** and **NOT default to summarization**.

### Test Queries:
```
/ask who talked about geopolitics
/ask tell me about the API
/ask what is Docker
/ask who mentioned Python
/ask find messages about deployment
/ask discussions about React
/ask what happened with the database
/ask who discussed the new feature
```

### Expected Behavior:
- ✅ Intent: `lookup`
- ✅ Searches entire history (not just 3 days)
- ✅ Uses hybrid search (BM25 + Vector + Graph)
- ✅ Reranks results
- ✅ Returns messages about the specific topic
- ✅ Citations: `[Author in #channel]`

---

## 👤 **2. USER_MESSAGES INTENT** (User-Specific Queries)

These should search messages **FROM** a specific user across entire history.

### Test Queries & Expected Outputs:

1. **`/ask what did @Roop say`**
   - User-specific messages about a specific topic the user specifies
   - Returns: Messages from @Roop (general summary of what they discussed)

2. **`/ask what is @user trying to convey`**
   - Explain what the user is trying to communicate
   - Returns: Analysis of the user's intent and message themes

3. **`/ask messages from @john`**
   - Summary from the author
   - Returns: Overview of @john's messages and topics

4. **`/ask what do you know about @alice`**
   - Personality summary
   - Returns: Profile based on @alice's interests, expertise, communication style

5. **`/ask @bob's messages about the API`**
   - User-specific messages filtered by topic
   - Returns: Summary of @bob's messages specifically about the API

6. **`/ask tell me about @user`**
   - Personality summary
   - Returns: Comprehensive profile of the user based on their messages

### Expected Behavior:
- ✅ Intent: `user_messages`
- ✅ Searches entire history (not just 3 days)
- ✅ Filters by author_id
- ✅ Returns messages FROM that user
- ✅ Generates personality/activity summaries, not just message lists
- ✅ No time limit (searches all time)

---

## 🧠 **3. EXPERT_FINDING INTENT** (Who Knows What)

These should find people who discussed a topic.

### Test Queries:
```
/ask who knows Python
/ask who is expert in React
/ask who can help with deployment
/ask who talked about Docker
```

### Expected Behavior:
- ✅ Intent: `expert_finding` or `lookup`
- ✅ Returns list of people
- ✅ Shows discussion frequency
- ✅ Ranked by expertise/mentions

---

## 📊 **4. SUMMARIZATION INTENT** (General Server Activity)

These should ONLY trigger for general activity with NO specific topic.

### Test Queries:
```
/ask what did i miss
/ask what happened
/ask server activity
/ask recent activity
/ask what's new
```

### Expected Behavior:
- ✅ Intent: `summarization`
- ✅ Searches last 3 days
- ✅ General overview of server activity
- ✅ No specific entity filter

---

## 🔗 **5. RELATIONAL INTENT** (How X Relates to Y)

These should explore relationships between entities.

### Test Queries:
```
/ask how are Docker and Kubernetes related
/ask connection between API and database
/ask relationship between @user1 and @user2
```

### Expected Behavior:
- ✅ Intent: `relational`
- ✅ Graph traversal to find connections
- ✅ Shows relationship path
- ✅ Explains how entities are connected

---

## ⏱️ **6. TEMPORAL_CONTEXT INTENT** (Evolution Over Time)

These should show how something changed over time.

### Test Queries:
```
/ask how did the API evolve over time
/ask what happened with deployment over the weeks
/ask evolution of the database schema
```

### Expected Behavior:
- ✅ Intent: `temporal_context`
- ✅ Chronological ordering
- ✅ Shows changes over time
- ✅ Temporal connections highlighted

---

## 💬 **7. CONVERSATION_THREADS INTENT** (Discussion Threads)

These should find conversation threads.

### Test Queries:
```
/ask continue the discussion about API
/ask thread about deployment
/ask conversation about the bug fix
```

### Expected Behavior:
- ✅ Intent: `conversation_threads`
- ✅ Shows message sequences
- ✅ Conversation flow preserved
- ✅ Multiple participants shown

---

## ❓ **8. FAQ QUERIES** (Static Responses)

These should bypass RAG pipeline and return static FAQ responses.

### Test Queries:
```
/ask hello
/ask hi tealdr
/ask help
/ask what can you do
/ask how to use this
/ask what is tealdr
/ask commands
/ask how to search
```

### Expected Behavior:
- ✅ Instant response (no RAG pipeline)
- ✅ Static FAQ content
- ✅ No database search
- ✅ Helpful guidance provided

---

## 🧪 **9. EDGE CASES** (Test Robustness)

### Empty Results:
```
/ask nonexistent topic that was never discussed
/ask messages from @fakeusernotinserver
```
**Expected:** "No Relevant Messages Found" with suggestions

### Ambiguous Queries:
```
/ask it
/ask that thing
/ask you know what i mean
```
**Expected:** Attempts lookup, may return low-confidence results or ask for clarification

### Complex Queries:
```
/ask what did @user say about Docker and Kubernetes in the last week
/ask who discussed API deployment in #dev channel
```
**Expected:** Multiple filters applied (user + topic + channel + time)

---

## 📋 **10. PIPELINE COMPONENT TESTS**

### Test RRF Fusion:
```
/ask deployment
```
**Check logs for:** "Hybrid search returned X fused results"

### Test Reranking:
```
/ask API configuration
```
**Check logs for:** "Reranking complete: X results"

### Test Compression:
```
/ask everything about Docker
```
**Check logs for:** "Compression complete: X results within token budget"

### Test CRAG Refinement:
```
/ask vague topic with low confidence
```
**Check logs for:** Query refinement if initial results are weak

---

## 🔍 **11. INTENT ROUTING VALIDATION**

### Should be LOOKUP (not summarization):
```
/ask who talked about geopolitics ✅ lookup
/ask tell me about the API ✅ lookup
/ask what is Docker ✅ lookup
/ask discussions about Python ✅ lookup
```

### Should be SUMMARIZATION:
```
/ask what did i miss ✅ summarization
/ask what happened ✅ summarization
/ask server activity ✅ summarization
```

### Should be USER_MESSAGES:
```
/ask what did @user say ✅ user_messages
/ask messages from @alice ✅ user_messages
```

---

## 📊 **12. EXPECTED LOG PATTERNS**

### Successful Query Flow:
```
[INFO] Hybrid search query: 'deployment'
[INFO] Hybrid search returned 15 fused results
[INFO] Reranking complete: 15 results
[INFO] Compression complete: 10 results within token budget
[INFO] Context assembled: 10 items (3 graph, 7 vector)
[INFO] Answer generated (450 chars) for query: deployment
```

### Intent Detection:
```
[INFO] Query understood: intent=lookup, entity=Docker
[INFO] Detected specific query, using lookup intent
```

### RRF Fusion:
```
[INFO] RRF fusion: 10 BM25, 12 vector, 5 graph results
[INFO] RRF fusion complete: 18 unique documents
[INFO]   Top 1: RRF=0.0487, sources=['bm25_rank_1', 'vector_rank_3', 'graph_rank_1']
```

---

## ✅ **VALIDATION CHECKLIST**

After running test queries, verify:

- [ ] **Intent Routing**: Specific queries → lookup (NOT summarization)
- [ ] **Hybrid Search**: BM25 + Vector + Graph all contributing
- [ ] **RRF Fusion**: Multiple retrievers being merged
- [ ] **Reranking**: Results being reordered by relevance
- [ ] **Compression**: Token budget being enforced
- [ ] **Citations**: Inline format `[Author in #channel]`
- [ ] **No Hallucinations**: All facts from retrieved messages
- [ ] **Uncertainty**: Model says "I couldn't find..." when no results
- [ ] **FAQ Bypass**: Common questions get instant static responses
- [ ] **User Queries**: Search entire history, not just 3 days

---

## 🚨 **KNOWN ISSUES TO WATCH FOR**

1. **Defaulting to Summarization**: If specific queries get `intent=summarization`, the intent router is broken
2. **3-Day Limit on User Queries**: If user queries only search 3 days, the safety check isn't working
3. **No RRF Fusion**: If logs don't show "RRF fusion complete", hybrid search isn't running
4. **No Reranking**: If logs don't show "Reranking complete", reranker isn't integrated
5. **Hallucinations**: If bot invents facts not in messages, RAG grounding is broken

---

## 📈 **SUCCESS METRICS**

- **Intent Accuracy**: >90% of queries classified correctly
- **Retrieval Quality**: >80% of results relevant to query
- **Response Time**: <5 seconds end-to-end
- **Citation Coverage**: 100% of facts cited with sources
- **Zero Hallucinations**: 0% fabricated information
- **FAQ Hit Rate**: Common questions bypass RAG (instant response)

---

## 🎯 **QUICK TEST SEQUENCE**

Run these 10 queries in order to validate the complete pipeline:

1. `/ask hello` → FAQ response (instant)
2. `/ask who talked about Docker` → lookup intent, hybrid search
3. `/ask what did @user say` → user_messages intent, full history
4. `/ask what did i miss` → summarization intent, 3 days
5. `/ask tell me about the API` → lookup intent, NOT summarization
6. `/ask who knows Python` → expert_finding/lookup
7. `/ask nonexistent topic` → empty results, helpful suggestions
8. `/ask deployment` → check logs for RRF, reranking, compression
9. `/ask what is Kubernetes` → lookup with citations
10. `/ask help` → FAQ response (instant)

**All 10 should work correctly with the new pipeline!** ✅
