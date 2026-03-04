#!/bin/bash
# Post-Deployment Verification Script
# Run this on the VM after deployment to verify RAG improvements are working

echo "=========================================="
echo "RAG Improvements - Deployment Verification"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
PASSED=0
FAILED=0

# Function to check and report
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $1"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: $1"
        ((FAILED++))
    fi
}

echo "1. Checking file deployments..."
echo "-----------------------------------"

# Check modified files exist
test -f ai/gemini_client.py
check "ai/gemini_client.py exists"

test -f retrieval/vector_search.py
check "retrieval/vector_search.py exists"

test -f database/supabase_client.py
check "database/supabase_client.py exists"

test -f bot/commands.py
check "bot/commands.py exists"

# Check new files exist
test -f ingestion/summarizer.py
check "ingestion/summarizer.py exists"

test -f utils/background_jobs.py
check "utils/background_jobs.py exists"

test -f database/migrations/001_add_bm25_support.sql
check "Migration 001 exists"

test -f database/migrations/002_add_channel_summaries.sql
check "Migration 002 exists"

echo ""
echo "2. Checking code changes..."
echo "-----------------------------------"

# Check for anti-hallucination instruction
grep -q "ANTI_HALLUCINATION_INSTRUCTION" ai/gemini_client.py
check "Anti-hallucination instruction added"

# Check for confidence threshold
grep -q "CONFIDENCE_THRESHOLD = 0.35" retrieval/vector_search.py
check "Confidence threshold constant added"

# Check for BM25 search
grep -q "async def bm25_search" database/supabase_client.py
check "BM25 search function added"

# Check for hybrid search
grep -q "async def hybrid_search" database/supabase_client.py
check "Hybrid search function added"

# Check for channel summaries
grep -q "async def store_channel_summary" database/supabase_client.py
check "Store channel summary function added"

grep -q "async def get_channel_summaries" database/supabase_client.py
check "Get channel summaries function added"

# Check for summarizer
grep -q "async def summarize_channel_hour" ingestion/summarizer.py
check "Summarize channel hour function added"

# Check for background jobs
grep -q "class BackgroundJobScheduler" utils/background_jobs.py
check "Background job scheduler added"

echo ""
echo "3. Checking Docker container..."
echo "-----------------------------------"

# Check if container is running
sudo docker-compose ps | grep -q "Up"
check "Docker container is running"

# Check logs for startup messages
sudo docker-compose logs --tail=50 | grep -q "Gemini client initialized"
check "Gemini client initialized"

sudo docker-compose logs --tail=50 | grep -q "Supabase client initialized"
check "Supabase client initialized"

echo ""
echo "4. Checking database migrations..."
echo "-----------------------------------"

# Note: These require database access - skip if not configured
echo -e "${YELLOW}Note: Database checks require Supabase credentials${NC}"
echo "Run these manually in Supabase SQL Editor:"
echo ""
echo "-- Check tsvector column"
echo "SELECT column_name FROM information_schema.columns WHERE table_name = 'messages' AND column_name = 'content_tsv';"
echo ""
echo "-- Check channel_summaries table"
echo "SELECT table_name FROM information_schema.tables WHERE table_name = 'channel_summaries';"
echo ""

echo ""
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Deployment successful.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run database migrations (see DEPLOYMENT_GUIDE.md)"
    echo "2. Test /ask command in Discord"
    echo "3. Test /lookup command in Discord"
    echo "4. Monitor logs for 24 hours"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Review errors above.${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check deployment logs: sudo docker-compose logs --tail=200"
    echo "2. Verify all files were copied correctly"
    echo "3. Review DEPLOYMENT_GUIDE.md"
    exit 1
fi
