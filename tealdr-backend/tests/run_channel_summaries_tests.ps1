# PowerShell script to run channel summaries tests
# Tests P1.5-P1.7: Hourly summarization and /recap integration

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running Channel Summaries Tests (P1.5-P1.7)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Run the tests
Write-Host "Running pytest for channel summaries features..." -ForegroundColor Yellow
Write-Host ""

pytest tests/test_channel_summaries.py -v --tb=short

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "All Channel Summaries Tests Passed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "P1.5-P1.7 Implementation Summary:" -ForegroundColor Cyan
    Write-Host "  - Channel summaries table: CREATED" -ForegroundColor Green
    Write-Host "  - Hourly summarization job: IMPLEMENTED" -ForegroundColor Green
    Write-Host "  - /recap integration: IMPLEMENTED" -ForegroundColor Green
    Write-Host "  - All tests passing: YES" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Run database migration: .\database\migrations\run_migration.ps1 -MigrationFile '002_add_channel_summaries.sql'" -ForegroundColor White
    Write-Host "  2. Enable background jobs in main.py" -ForegroundColor White
    Write-Host "  3. Deploy and test on VM" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Some Tests Failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
