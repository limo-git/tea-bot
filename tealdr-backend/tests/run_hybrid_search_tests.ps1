# PowerShell script to run hybrid search tests
# Tests P1.2: BM25 + Vector hybrid search with RRF

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running Hybrid Search Tests (P1.2)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Run the tests
Write-Host "Running pytest for hybrid search features..." -ForegroundColor Yellow
Write-Host ""

pytest tests/test_hybrid_search.py -v --tb=short

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "All Hybrid Search Tests Passed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "P1.2 Implementation Summary:" -ForegroundColor Cyan
    Write-Host "  - BM25 full-text search: IMPLEMENTED" -ForegroundColor Green
    Write-Host "  - Reciprocal Rank Fusion: IMPLEMENTED" -ForegroundColor Green
    Write-Host "  - Hybrid search function: IMPLEMENTED" -ForegroundColor Green
    Write-Host "  - All tests passing: YES" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Run database migration: .\database\migrations\run_migration.ps1 -MigrationFile '001_add_bm25_support.sql'" -ForegroundColor White
    Write-Host "  2. Integrate hybrid search into /lookup command" -ForegroundColor White
    Write-Host "  3. Deploy and test on VM" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Some Tests Failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
