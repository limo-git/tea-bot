# New /ask Command Filter Parameters

**Date:** March 5, 2026  
**Status:** ✅ Complete - Ready for Deployment

---

## 🎯 **What Was Added**

Added two new optional parameters to the `/ask` command for more precise message filtering:

1. **`from_user`** - Filter messages FROM a specific user
2. **`mentions`** - Filter messages that MENTION a specific user

---

## 📝 **Parameter Details**

### **from_user: discord.User**
- **Type:** Discord User (select from dropdown)
- **Purpose:** Show only messages authored by the specified user
- **Priority:** Overrides @mentions in the query text
- **Example:** `/ask query:"what did alice say" from_user:@alice`

### **mentions: discord.User**
- **Type:** Discord User (select from dropdown)
- **Purpose:** Show only messages that mention the specified user
- **Example:** `/ask query:"who mentioned bob" mentions:@bob`

### **Combined Usage**
Both parameters can be used together for advanced filtering:
- **Example:** `/ask query:"what did alice say about bob" from_user:@alice mentions:@bob`
- **Result:** Shows messages FROM alice that MENTION bob

---

## 🔧 **Implementation Details**

### **Modified Files (5)**

1. **`bot/commands.py`**
   - Added `from_user` and `mentions` parameters to command signature
   - Priority logic: `from_user` parameter > query @mention > context
   - Passes `mentions_user_id` to query pipeline

2. **`retrieval/query_engine.py`**
   - Added `mentions_user_id` parameter to `run_query_pipeline()`
   - Passes through to vector search

3. **`retrieval/vector_search.py`**
   - Added `mentions_user_id` parameter to `vector_search()`
   - Passes to database layer

4. **`database/supabase_client.py`**
   - Added `mentions_user_id` parameter to `semantic_search_filtered()`
   - Post-query filtering for mention patterns: `<@user_id>` and `<@!user_id>`

5. **`tests/test_ask_command_filters.py`** (New)
   - 6 tests covering both parameters
   - Tests parameter passing and filtering logic

---

## 💡 **Usage Examples**

### **Example 1: Messages from a specific user**
```
/ask query:what links did limo share from_user:@limo
```
**Result:** Only shows messages authored by limo

### **Example 2: Messages mentioning a user**
```
/ask query:who talked about alice mentions:@alice
```
**Result:** Shows all messages that mention @alice

### **Example 3: Combined filtering**
```
/ask query:what did bob say about the deployment from_user:@bob mentions:@alice
```
**Result:** Shows messages FROM bob that MENTION alice

### **Example 4: With other filters**
```
/ask query:recent discussions from_user:@alice in_channel:#general from_date:2026-03-01
```
**Result:** Messages from alice in #general since March 1st

---

## 🎨 **User Experience**

### **Before (Old Behavior)**
```
User: /ask query:what @limo is trying to convey by sending links
Bot: [Returns messages from multiple users mentioning limo AND messages from limo]
```

### **After (New Behavior)**
```
User: /ask query:what did limo say from_user:@limo
Bot: [Returns ONLY messages from limo]
```

**OR**

```
User: /ask query:who mentioned limo mentions:@limo
Bot: [Returns ONLY messages that mention @limo]
```

---

## 🔍 **How It Works**

### **from_user Parameter Flow**

1. User selects a user from Discord dropdown
2. Command extracts user ID
3. Passed as `author_id` to query pipeline
4. Database filters: `WHERE author_id = ?`
5. Only messages from that user are returned

### **mentions Parameter Flow**

1. User selects a user from Discord dropdown
2. Command extracts user ID
3. Passed as `mentions_user_id` to query pipeline
4. Database retrieves messages, then filters for:
   - `<@user_id>` (standard mention)
   - `<@!user_id>` (nickname mention)
5. Only messages containing those patterns are returned

---

## 📊 **Complete /ask Parameter List**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `query` | String | Your question (required) | `"what happened yesterday"` |
| `in_channel` | Channel | Filter by channel | `#general` |
| `in_thread` | Thread | Filter by thread | `Thread: Bug Discussion` |
| **`from_user`** | **User** | **Filter by author** | **`@alice`** |
| **`mentions`** | **User** | **Filter by mentioned user** | **`@bob`** |
| `from_date` | String | Start date (YYYY-MM-DD) | `2026-03-01` |
| `to_date` | String | End date (YYYY-MM-DD) | `2026-03-05` |
| `min_length` | Integer | Minimum message length | `100` |
| `server_name` | String | Server name (DM use) | `My Server` |

---

## 🐛 **Bug Fixes Included**

### **Fixed: User Mention Filtering Bug**
- **Problem:** Queries like "what @user said" returned messages from other users
- **Cause:** System treated user mentions as entities to search for, not author filters
- **Solution:** Added `user_messages` intent that correctly filters by `author_id`
- **Tests:** 8 tests in `test_user_mention_filtering.py`

---

## ✅ **Testing**

### **Test Coverage**
- ✅ `from_user` parameter filters by author (2 tests)
- ✅ `mentions` parameter filters by mentioned user (2 tests)
- ✅ Both parameters can be combined (1 test)
- ✅ Mention pattern matching (both `<@id>` and `<@!id>`) (1 test)

### **Manual Testing Checklist**
- [ ] `/ask query:"test" from_user:@user` returns only that user's messages
- [ ] `/ask query:"test" mentions:@user` returns only messages mentioning that user
- [ ] Combined filters work correctly
- [ ] Parameters work with existing filters (channel, date, etc.)
- [ ] Dropdown user selection works in Discord UI

---

## 🚀 **Deployment**

### **No Database Changes Required**
- Uses existing `author_id` column for `from_user`
- Uses existing `content` column for `mentions` (text search)

### **Deployment Steps**
1. Deploy updated code to VM
2. Restart bot: `sudo docker-compose restart`
3. Discord will automatically sync new command parameters
4. Test with `/ask` command

### **Verification**
```bash
# Check logs for new parameters
sudo docker-compose logs --tail=100 | grep "Filtering by"

# Should see:
# "Filtering by user (from): <username>"
# "Filtering by mentions: <username>"
```

---

## 📚 **Related Documentation**

- **User Mention Bug Fix:** `tests/test_user_mention_filtering.py`
- **Complete RAG Implementation:** `COMPLETE_RAG_IMPLEMENTATION.md`
- **P2 Entity Improvements:** `P2_ENTITY_IMPROVEMENTS.md`

---

## 🎓 **Key Learnings**

1. **Parameter Priority Matters** - Explicit parameters should override query text
2. **Post-Query Filtering** - Mention filtering done after DB query for flexibility
3. **Both Mention Formats** - Discord uses `<@id>` and `<@!id>` for mentions
4. **User Experience** - Dropdown selection is clearer than text parsing

---

**Implementation Complete:** March 5, 2026  
**Ready for Production:** ✅ Yes  
**Breaking Changes:** None
