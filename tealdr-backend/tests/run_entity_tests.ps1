# PowerShell script to run entity improvement tests
# Tests P2: Entity extraction improvements and expert threshold

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running Entity Improvement Tests (P2)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Run the tests
Write-Host "Running pytest for entity improvement features..." -ForegroundColor Yellow
Write-Host ""

pytest tests/test_entity_improvements.py -v --tb=short

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "All Entity Improvement Tests Passed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "P2 Implementation Summary:" -ForegroundColor Cyan
    Write-Host "  - Entity quality scoring: IMPLEMENTED" -ForegroundColor Green
    Write-Host "  - Entity validation: IMPLEMENTED" -ForegroundColor Green
    Write-Host "  - Entity deduplication: IMPLEMENTED" -ForegroundColor Green
    Write-Host "  - Expert confidence scores: IMPLEMENTED" -ForegroundColor Green
    Write-Host "  - All tests passing: YES" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Run all tests: pytest tests/ -v" -ForegroundColor White
    Write-Host "  2. Deploy to VM" -ForegroundColor White
    Write-Host "  3. Monitor entity extraction quality" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Some Tests Failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
