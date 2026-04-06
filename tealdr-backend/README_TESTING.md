# Comprehensive RAG Pipeline Testing Guide

## Overview

This test suite validates all 5 RAG pipelines in TealDR Bot with 35 comprehensive test cases covering:
- **Naive Vector RAG** - Basic semantic search
- **Hybrid BM25** - Exact term matching + semantic search
- **Graph RAG** - Entity relationships and expert finding
- **Hierarchical RAG** - Time-scoped summaries
- **Agentic/CRAG** - Self-aware uncertainty and anti-hallucination

## Quick Start

### 1. Run the Tests

```powershell
.\run_comprehensive_tests.ps1
```

Or manually:

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run tests
python tests\comprehensive_rag_test.py
```

### 2. Review Results

The test suite generates two output files:

- **`test_results_YYYYMMDD_HHMMSS.txt`** - Human-readable report
- **`test_results_YYYYMMDD_HHMMSS.json`** - Machine-readable data

## What Gets Tested

### Section 1: Naive Vector RAG (4 tests)
- ✅ Basic semantic lookup with natural language
- ✅ Synonym handling and semantic equivalence
- ✅ Relevance threshold and weak match rejection
- ✅ Multi-concept query combining topics

### Section 2: Hybrid BM25 (5 tests)
- ✅ Exact username lookup (critical)
- ✅ Version numbers and technical terms (critical)
- ✅ Combined exact + semantic search (critical)
- ✅ Channel name exact matching
- ✅ Acronyms and shorthand (PR, LGTM, etc.)

### Section 3: Graph RAG (2 tests)
- ✅ Expert finding with message counts (critical)
- ✅ Multi-hop entity relationships (critical)

### Section 5: Agentic/CRAG (4 tests)
- ✅ "I don't know" test - admits knowledge gaps (critical)
- ✅ Low evidence uncertainty expression (critical)
- ✅ Confidence gating for borderline queries (critical)
- ✅ Source-constrained generation (critical)

## Understanding Results

### Pass/Fail Criteria

**✅ PASS** - Test met all validation criteria
**❌ FAIL** - Test failed validation but executed
**⚠️ ERROR** - Test encountered an exception

### Critical Tests

Tests marked **[CRITICAL]** represent dangerous failure modes:
- Exact term misses (BM25 not working)
- Expert hallucination (false expertise claims)
- Fabricated answers (hallucination)
- Data leaks (cross-server contamination)

**Fix critical failures immediately before other improvements.**

## Sample Output

```
================================================================================
TealDR Bot - Comprehensive RAG Pipeline Test Report
================================================================================
Generated: 2026-03-07 15:30:45 UTC
Server ID: 1131555356418523180
Total Execution Time: 45.23s

SUMMARY
--------------------------------------------------------------------------------
Total Tests: 15
✅ Passed: 12 (80.0%)
❌ Failed: 2 (13.3%)
⚠️  Errors: 1 (6.7%)
🔴 Critical Failures: 1

Hybrid BM25 Pipeline
--------------------------------------------------------------------------------
Pass Rate: 4/5 (80.0%)

✅ Test 2.1: Exact username lookup [CRITICAL]
   Query: sidtheitguy
   Type: lookup
   Status: PASS
   Execution Time: 1.23s
   Validation: Found 8/10 top results matching 'sidtheitguy'
   Sources Found: 47

❌ Test 2.3: Combined exact + semantic [CRITICAL]
   Query: what did sidtheitguy say about docker?
   Type: ask
   Status: FAIL
   Execution Time: 2.45s
   Validation: No messages from sidtheitguy in top results - BM25 not fusing
   Sources Found: 23
```

## Configuration

The test suite automatically discovers:
- **Usernames** - From recent messages in your server
- **Topics** - Common technical terms found in messages
- **Server ID** - Configured in the script (default: 1131555356418523180)

### Customizing Server ID

Edit `tests/comprehensive_rag_test.py`:

```python
async def main():
    SERVER_ID = 1131555356418523180  # Change this to your server ID
```

## Validation Logic

Each test includes a validation function that checks:

### `validate_semantic_lookup`
- Results returned
- Similarity scores present
- Top results above 0.3 threshold

### `validate_exact_username`
- Username identified in query
- Top 10 results contain username
- BM25 exact matching working

### `validate_no_hallucination`
- Uncertainty phrases when evidence is low
- No confident answers with zero sources
- Appropriate hedging for borderline queries

### `validate_source_accuracy`
- Specific claims supported by sources
- Answer length proportional to evidence
- No fabricated details

### `validate_multi_concept`
- All query concepts found in sources
- Results combine topics, not just list separately

## Interpreting Failures

### Common Failure Patterns

**"No results returned"**
- Embedding generation failed
- Database connection issue
- Server has no indexed messages

**"Top similarity too low"**
- Query doesn't match server content
- Embeddings not properly indexed
- Semantic search threshold too high

**"No uncertainty expressed"**
- CRAG pipeline not active
- Confidence gating disabled
- Hallucination risk - fix immediately

**"BM25 not fusing"**
- Hybrid search not enabled
- RRF fusion broken
- Exact terms being ignored

## Next Steps After Testing

### If All Tests Pass ✅
- RAG pipelines functioning correctly
- Safe to deploy to production
- Monitor for edge cases in real usage

### If Critical Tests Fail 🔴
1. **Stop** - Do not deploy
2. **Fix** - Address critical failures first
3. **Re-test** - Run suite again
4. **Verify** - Manual testing in Discord

### If Non-Critical Tests Fail ⚠️
- Review validation notes
- Check if failure is expected (e.g., topic not discussed)
- Improve pipeline if genuine issue
- Re-run specific tests

## Advanced Usage

### Run Specific Test Categories

Modify `run_all_tests()` to include only desired tests:

```python
tests = [
    # Only run critical tests
    ("2.1", "Exact username lookup", "Hybrid BM25", ...),
    ("5.1", "I don't know test", "Agentic/CRAG", ...),
]
```

### Add Custom Tests

```python
("X.1", "My custom test", "Pipeline Name",
 "test query here", "ask",  # or "lookup"
 self.validate_semantic_lookup,  # validation function
 True)  # critical flag
```

### Custom Validation Functions

```python
async def validate_my_test(self, result: Dict) -> tuple[bool, str]:
    """Custom validation logic."""
    sources = result.get('sources', [])
    
    # Your validation logic here
    if some_condition:
        return True, "Test passed because..."
    else:
        return False, "Test failed because..."
```

## Troubleshooting

### "Virtual environment not found"
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### "Database connection failed"
- Check `.env` file exists
- Verify `SUPABASE_URL` and `SUPABASE_KEY`
- Test database connectivity

### "No usernames found"
- Server has no indexed messages
- Run message indexing first
- Check server_id is correct

### "All tests error"
- Check logs for stack traces
- Verify all dependencies installed
- Ensure database schema is up to date

## Files

- `tests/comprehensive_rag_test.py` - Main test suite
- `run_comprehensive_tests.ps1` - PowerShell runner
- `test_results_*.txt` - Human-readable reports
- `test_results_*.json` - Machine-readable data

## Support

For issues or questions:
1. Check the generated report validation notes
2. Review logs for detailed error messages
3. Verify database connectivity and schema
4. Ensure all RAG pipelines are properly configured
