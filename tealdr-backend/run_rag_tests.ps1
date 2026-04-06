# PowerShell script to run RAG prompt rules tests
# Tests the implementation of strict RAG best practices

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "RAG PROMPT RULES TEST SUITE" -ForegroundColor Cyan
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

# Run the RAG prompt rules tests
Write-Host ""
Write-Host "Running RAG Prompt Rules Tests..." -ForegroundColor Green
Write-Host ""

python tests\test_rag_prompt_rules.py

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
