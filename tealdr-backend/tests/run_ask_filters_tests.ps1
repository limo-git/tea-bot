# PowerShell script to run /ask command filter tests
# Tests the new from_user and mentions parameters

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running /ask Command Filter Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Run the tests
Write-Host "Running pytest for /ask filter parameters..." -ForegroundColor Yellow
Write-Host ""

pytest tests/test_ask_command_filters.py -v --tb=short

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "All Filter Tests Passed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "New Parameters Summary:" -ForegroundColor Cyan
    Write-Host "  - from_user: Filter messages FROM a specific user" -ForegroundColor Green
    Write-Host "  - mentions: Filter messages that MENTION a specific user" -ForegroundColor Green
    Write-Host "  - Both can be combined for advanced filtering" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage Examples:" -ForegroundColor Yellow
    Write-Host "  /ask query:what did alice say from_user:@alice" -ForegroundColor White
    Write-Host "  /ask query:who mentioned bob mentions:@bob" -ForegroundColor White
    Write-Host "  /ask query:what did alice say about bob from_user:@alice mentions:@bob" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Deploy to VM" -ForegroundColor White
    Write-Host "  2. Test the new parameters in Discord" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Some Tests Failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
