# PowerShell script to run P3 CRAG refinement tests

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running P3: CRAG Refinement Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Run the tests
Write-Host "Running pytest for CRAG refinement..." -ForegroundColor Yellow
Write-Host ""

pytest tests/test_crag_refinement.py -v --tb=short

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "All P3 CRAG Tests Passed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "P3 CRAG Features:" -ForegroundColor Cyan
    Write-Host "  ✅ Confidence scoring for retrievals" -ForegroundColor Green
    Write-Host "  ✅ Automatic refinement trigger" -ForegroundColor Green
    Write-Host "  ✅ LLM-based query refinement" -ForegroundColor Green
    Write-Host "  ✅ Multi-query re-retrieval" -ForegroundColor Green
    Write-Host "  ✅ Result deduplication & sorting" -ForegroundColor Green
    Write-Host "  ✅ Answer quality assessment" -ForegroundColor Green
    Write-Host ""
    Write-Host "P3 Implementation Complete!" -ForegroundColor Yellow
    Write-Host "  - Extended conversation context ✅" -ForegroundColor Green
    Write-Host "  - CRAG refinement loop ✅" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Some Tests Failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
