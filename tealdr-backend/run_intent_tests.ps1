# PowerShell script to run intent routing tests
# Tests query classification and intent detection

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "INTENT ROUTING TEST SUITE" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create a virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Run the intent routing tests
Write-Host ""
Write-Host "Running Intent Routing Tests..." -ForegroundColor Green
Write-Host ""

python tests\test_intent_routing.py

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "======================================" -ForegroundColor Green
    Write-Host "ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
} else {
    Write-Host "======================================" -ForegroundColor Red
    Write-Host "SOME TESTS FAILED!" -ForegroundColor Red
    Write-Host "======================================" -ForegroundColor Red
}

Write-Host ""
Write-Host "Test execution complete." -ForegroundColor Cyan

exit $exitCode
