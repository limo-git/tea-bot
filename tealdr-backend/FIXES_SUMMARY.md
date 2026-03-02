# /ask Command Fixes - Complete Summary

## Issue: /ask Returns Feb 27 Data Instead of Most Recent (Mar 2)

### Root Causes Identified:

1. **Vector search had 7-day default instead of 3-day**
   - File: `retrieval/vector_search.py`
   - Old: `timedelta(days=7)`
   - New: `timedelta(days=3)`

2. **Supabase semantic search not ordering by timestamp**
   - File: `database/supabase_client.py`
   - Old: `query.limit(200).execute().data` (no ordering)
   - New: `query.order('created_at', desc=True).limit(200).execute().data`
   - Impact: Messages were sorted by semantic similarity only, not recency

3. **Supabase channel join error**
   - File: `database/supabase_client.py`
   - Old: `select('*, channels(name)')`
   - New: `select('*')` (no join)

4. **Neo4j datetime parsing errors**
   - File: `graph/queries.py`
   - Old: `duration.between(datetime(...))` causing parsing errors
   - New: Millisecond arithmetic `abs(m.timestamp - nearby.timestamp) / 3600000`

5. **Missing time_filter parameter in temporal engine**
   - File: `retrieval/temporal_engine.py`
   - Added: `time_range` parameter to `_get_primary_results()`
   - Added: Default 3-day time filter when no range provided

## How /recap vs /ask Differ:

### /recap Command:
- **Database**: Supabase only (PostgreSQL)
- **Query**: Direct SQL query with `get_messages_by_timerange()`
- **Ordering**: Always `ORDER BY created_at DESC`
- **Time range**: Exact 3-day window (Feb 27 - Mar 2)
- **Result**: Raw messages ordered by timestamp

### /ask Command:
- **Database**: Dual system (Neo4j + Supabase)
- **Query**: Graph RAG pipeline → Temporal engine → Vector search
- **Ordering**: 
  - Neo4j: `ORDER BY timestamp DESC` ✅
  - Supabase: Now `ORDER BY created_at DESC` ✅ (FIXED)
- **Time range**: 3-day window with semantic search
- **Result**: Context-aware messages with entity relationships

## Expected Behavior After Fixes:

When you run `/ask what did i miss out on while i was away?`:

**Before:**
- ❌ Returns Feb 27 as most recent
- ❌ Missing Feb 28, Mar 1, Mar 2 data
- ❌ Sorted by semantic similarity only
- ❌ 7-day time window

**After:**
- ✅ Returns Mar 2 as most recent (if data exists)
- ✅ Includes Feb 28, Mar 1, Mar 2 data
- ✅ Sorted by timestamp DESC (most recent first)
- ✅ 3-day time window (Feb 27 - Mar 2)

## Files Modified:

1. `retrieval/vector_search.py` - Changed 7-day to 3-day default
2. `database/supabase_client.py` - Added ORDER BY created_at DESC
3. `database/supabase_client.py` - Removed invalid channel join
4. `graph/queries.py` - Fixed datetime parsing with millisecond arithmetic
5. `retrieval/temporal_engine.py` - Added time_filter parameter
6. `retrieval/query_engine.py` - Updated time filtering logic
7. `bot/commands.py` - Added 3-day default for general queries

## Deployment Required:

All fixes are committed to git but need to be deployed to VM:

```bash
git add .
git commit -m "Fix /ask to return most recent data with proper ordering"
git push origin main
.\update-vm.ps1
```

## Testing:

After deployment, test with:
```
/ask what did i miss out on while i was away?
```

Should return messages from Mar 2, Mar 1, Feb 28, Feb 27 (in that order, most recent first).
