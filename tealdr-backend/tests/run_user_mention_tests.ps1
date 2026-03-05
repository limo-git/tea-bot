# PowerShell script to run user mention filtering tests
# Tests bug fix for user-specific queries returning messages from other users

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running User Mention Filtering Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Run the tests
Write-Host "Running pytest for user mention filtering..." -ForegroundColor Yellow
Write-Host ""

pytest tests/test_user_mention_filtering.py -v --tb=short

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "All User Mention Tests Passed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Bug Fix Summary:" -ForegroundColor Cyan
    Write-Host "  - Added 'user_messages' intent" -ForegroundColor Green
    Write-Host "  - Queries like 'what @user said' now filter by author" -ForegroundColor Green
    Write-Host "  - Only returns messages FROM the specified user" -ForegroundColor Green
    Write-Host "  - No longer returns messages from other users" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Deploy to VM" -ForegroundColor White
    Write-Host "  2. Test with: /ask what @limo is trying to convey" -ForegroundColor White
    Write-Host "  3. Verify only limo's messages appear in results" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Some Tests Failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
