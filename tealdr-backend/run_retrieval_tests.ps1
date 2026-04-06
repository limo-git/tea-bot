# PowerShell script to run retrieval pipeline tests
# Tests RRF fusion, hybrid search, reranking, and compression

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "RETRIEVAL PIPELINE TEST SUITE" -ForegroundColor Cyan
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

# Run the retrieval pipeline tests
Write-Host ""
Write-Host "Running Retrieval Pipeline Tests..." -ForegroundColor Green
Write-Host ""

python tests\test_retrieval_pipeline.py

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
