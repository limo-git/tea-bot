# PowerShell script to run all P0 anti-hallucination tests
# Tests P0.1 + P0.2: Complete anti-hallucination foundation

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running All P0 Anti-Hallucination Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Run all P0 tests
Write-Host "Running all P0 tests..." -ForegroundColor Yellow
Write-Host ""

pytest tests/test_anti_hallucination.py tests/test_confidence_threshold.py -v --tb=short

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "All P0 Tests Passed!" -ForegroundColor Green
    Write-Host "P0.1: I don't know instruction - PASS" -ForegroundColor Green
    Write-Host "P0.2: Confidence threshold (0.35) - PASS" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  - Deploy P0 changes to VM" -ForegroundColor Yellow
    Write-Host "  - Proceed to P1.1: BM25 hybrid search" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "✗ Some Tests Failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
