# PowerShell script to run comprehensive RAG tests
# Activates virtual environment and runs the test suite

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "TealDR Bot - Comprehensive RAG Pipeline Test Runner" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create a virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found!" -ForegroundColor Yellow
    Write-Host "Make sure your environment variables are set." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting test suite..." -ForegroundColor Green
Write-Host ""

# Run the test suite
python tests\comprehensive_rag_test.py

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=" -NoNewline -ForegroundColor Green
    Write-Host ("=" * 79) -ForegroundColor Green
    Write-Host "Tests completed successfully!" -ForegroundColor Green
    Write-Host "=" -NoNewline -ForegroundColor Green
    Write-Host ("=" * 79) -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "=" -NoNewline -ForegroundColor Red
    Write-Host ("=" * 79) -ForegroundColor Red
    Write-Host "Tests encountered errors. Check the output above." -ForegroundColor Red
    Write-Host "=" -NoNewline -ForegroundColor Red
    Write-Host ("=" * 79) -ForegroundColor Red
}

Write-Host ""
Write-Host "Check the generated test_results_*.txt file for detailed results." -ForegroundColor Cyan
