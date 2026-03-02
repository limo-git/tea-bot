# PowerShell script to run query relevance test suite

Write-Host "Query Relevance Test Suite" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Set up environment
$env:PYTHONPATH = $PWD

# Run the test suite
Write-Host "`nRunning comprehensive test suite..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

try {
    python tests/test_query_relevance.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nALL TESTS PASSED!" -ForegroundColor Green
        Write-Host "Query relevance fixes are working correctly!" -ForegroundColor Green
        Write-Host "`nReady to deploy with: .\update-vm.ps1" -ForegroundColor Cyan
        exit 0
    } else {
        Write-Host "`nSOME TESTS FAILED!" -ForegroundColor Red
        Write-Host "Please review the output above and fix any issues." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "`nERROR RUNNING TESTS: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
