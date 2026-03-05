# PowerShell script to run P3 extended conversation context tests

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running P3: Extended Context Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Run the tests
Write-Host "Running pytest for extended conversation context..." -ForegroundColor Yellow
Write-Host ""

pytest tests/test_extended_context.py -v --tb=short

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "All P3 Extended Context Tests Passed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "P3 Features Implemented:" -ForegroundColor Cyan
    Write-Host "  ✅ Source message anchoring" -ForegroundColor Green
    Write-Host "  ✅ Entity tracking across turns" -ForegroundColor Green
    Write-Host "  ✅ Context relevance scoring" -ForegroundColor Green
    Write-Host "  ✅ Enhanced multi-turn formatting" -ForegroundColor Green
    Write-Host "  ✅ Turn number tracking" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next: Implement P3 CRAG refinement loop" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Some Tests Failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
