# /ask Command Fixes - Test Documentation

## Overview
This test suite validates the critical fixes applied to the `/ask` command system to resolve issues with:
1. Supabase channel join errors
2. Neo4j datetime parsing errors
3. Missing time_filter parameters
4. Recent data filtering (3-day default)

## Test Files

### `test_ask_command_fixes.py`
Comprehensive test suite covering all recent fixes to the `/ask` command.

## Test Categories

### 1. Supabase Channel Handling Tests
**Purpose**: Verify that Supabase queries work without attempting invalid channel joins.

**Test Cases**:
- `test_semantic_search_without_channel_join`: Ensures semantic search doesn't try to join channels table
- `test_context_assembler_handles_channel_id`: Verifies context assembler properly formats channel_id

**What Was Fixed**:
- Removed `channels(name)` join from Supabase query
- Updated context assembler to use channel_id directly
- Format channel_id as `#123456789` for display

**Expected Behavior**:
- ✅ No "Could not find a relationship between 'messages' and 'channels'" errors
- ✅ Vector search returns results successfully
- ✅ Channel IDs are properly formatted in context

---

### 2. Neo4j Datetime Parsing Tests
**Purpose**: Verify that Neo4j queries use safe datetime calculations without parsing errors.

**Test Cases**:
- `test_temporal_context_query_time_gap_calculation`: Checks temporal context uses millisecond arithmetic
- `test_conversation_threads_query_time_gap_calculation`: Checks conversation threads use millisecond arithmetic
- `test_summarization_query_datetime_comparison`: Verifies proper datetime() function usage

**What Was Fixed**:
- Replaced `duration.between(datetime(...))` with millisecond arithmetic
- Changed to `abs(m1.timestamp - m2.timestamp) / 86400000` for days
- Changed to `abs(m.timestamp - nearby.timestamp) / 3600000` for hours
- Added `datetime()` function calls for proper Neo4j datetime comparison

**Expected Behavior**:
- ✅ No "Text cannot be parsed to a DateTime" errors
- ✅ Time gap calculations work correctly
- ✅ Temporal context queries execute successfully

---

### 3. Time Filter Parameter Tests
**Purpose**: Verify that time_filter parameter is properly passed through the temporal engine.

**Test Cases**:
- `test_temporal_engine_passes_time_filter`: Ensures time_filter is passed to Neo4j queries
- `test_temporal_engine_default_time_filter`: Verifies 3-day default when no time_range provided

**What Was Fixed**:
- Added `time_range` parameter to `_get_primary_results()` function
- Added time_filter logic with 3-day default
- Updated temporal engine to pass time_range to primary results

**Expected Behavior**:
- ✅ No "Expected parameter(s): time_filter" errors
- ✅ Time filter defaults to 3 days for general queries
- ✅ Custom time ranges are properly applied

---

### 4. Recent Data Filtering Tests
**Purpose**: Verify that `/ask` command returns recent data (past 3 days) instead of old data.

**Test Cases**:
- `test_ask_command_applies_3day_filter`: Checks 3-day filter for general server queries
- `test_graph_traversal_uses_time_filter`: Verifies graph_traversal uses time_filter

**What Was Fixed**:
- Added 3-day time range detection for general server activity queries
- Updated graph_traversal to accept and use time_range parameter
- Changed default from 7 days to 3 days

**Expected Behavior**:
- ✅ General queries like "what did i miss" get 3-day filter
- ✅ Returns March 2026 data instead of February 2026 data
- ✅ Behaves like `/recap` for general server queries

---

### 5. Integration Tests
**Purpose**: Verify complete end-to-end flow of `/ask` command with all fixes applied.

**Test Cases**:
- `test_complete_ask_flow_with_recent_data`: Tests full pipeline with recent data filtering
- `test_error_handling_for_invalid_queries`: Tests edge cases and error handling

**Expected Behavior**:
- ✅ Complete pipeline executes without errors
- ✅ Recent data is returned (past 3 days)
- ✅ Temporal connections are made
- ✅ Edge cases are handled gracefully

---

## Running the Tests

### Run All Tests
```bash
cd tests
python test_ask_command_fixes.py
```

### Expected Output
```
🧪 Running /ask Command Fixes Test Suite
============================================================

📦 Testing Supabase Channel Handling...
✅ Supabase semantic search works without channel join
✅ Context assembler handles channel_id correctly

⏰ Testing Neo4j Datetime Parsing...
✅ Temporal context query uses safe time gap calculation
✅ Conversation threads query uses safe time gap calculation
✅ Summarization query uses proper datetime comparison

🔧 Testing Time Filter Parameter...
✅ Temporal engine passes time_filter parameter
✅ Temporal engine uses 3-day default time filter

📅 Testing Recent Data Filtering...
✅ /ask command applies 3-day filter for general queries
✅ graph_traversal uses time_filter parameter

🔗 Testing Integration Scenarios...
✅ Complete /ask flow works with recent data filtering
✅ Error handling works for edge cases

============================================================
🎉 All tests passed successfully!
============================================================
```

---

## Verification Checklist

After deployment, verify these behaviors in Discord:

### ✅ Supabase Channel Handling
- [ ] `/ask what did i miss?` returns results without database errors
- [ ] Channel IDs are displayed (e.g., `#123456789`)
- [ ] No "Could not find a relationship" errors in logs

### ✅ Neo4j Datetime Parsing
- [ ] No "Text cannot be parsed to a DateTime" errors in logs
- [ ] Temporal context queries execute successfully
- [ ] Time gaps are calculated correctly

### ✅ Time Filter Parameter
- [ ] No "Expected parameter(s): time_filter" errors in logs
- [ ] Graph traversal returns results
- [ ] Primary results are retrieved successfully

### ✅ Recent Data Filtering
- [ ] `/ask what did i miss?` returns data from past 3 days
- [ ] Returns March 2026 data (not old February data)
- [ ] Behaves like `/recap time:3d` for general queries

### ✅ Integration
- [ ] Complete `/ask` flow works end-to-end
- [ ] Both graph and vector results are returned
- [ ] Answer generation includes recent context
- [ ] No "null" entity errors

---

## Troubleshooting

### If tests fail:

1. **Check dependencies**: Ensure all required packages are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Check imports**: Verify all modules can be imported
   ```python
   python -c "from database.supabase_client import SupabaseClient"
   python -c "from retrieval.temporal_engine import run_temporal_query_pipeline"
   ```

3. **Check environment**: Ensure .env file has required variables
   ```bash
   GRAPH_RAG_ENABLED=true
   NEO4J_URI=bolt://localhost:7687
   SUPABASE_URL=https://...
   ```

4. **Run individual test classes**: Isolate failing tests
   ```python
   # In test_ask_command_fixes.py
   asyncio.run(TestSupabaseChannelHandling().test_semantic_search_without_channel_join())
   ```

---

## Related Files

### Modified Files
- `database/supabase_client.py` - Removed channel join
- `retrieval/context_assembler.py` - Updated channel_id handling
- `retrieval/temporal_engine.py` - Added time_filter parameter
- `retrieval/query_engine.py` - Updated time filtering logic
- `graph/queries.py` - Fixed datetime parsing in queries
- `bot/commands.py` - Added 3-day filter for general queries

### Test Files
- `tests/test_ask_command_fixes.py` - This test suite
- `tests/test_temporal_graph_rag.py` - Original temporal tests
- `tests/test_discord_integration.py` - Discord integration tests

---

## Success Criteria

All tests must pass before deployment:
- ✅ All 12 test cases pass
- ✅ No errors in test output
- ✅ Integration tests complete successfully
- ✅ Edge cases are handled properly

After deployment:
- ✅ `/ask` command returns recent data
- ✅ No database or Neo4j errors in logs
- ✅ Users receive helpful responses
- ✅ System behaves like `/recap` for general queries
