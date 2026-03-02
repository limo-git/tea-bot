# PowerShell script to run /ask command fixes test suite

Write-Host "🧪 /ask Command Fixes Test Suite" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Set up environment
$env:PYTHONPATH = "$PWD"

# Run the test suite
Write-Host "`n🔍 Running comprehensive test suite..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

try {
    python tests/test_ask_command_fixes.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ ALL TESTS PASSED!" -ForegroundColor Green
        Write-Host "Your /ask command fixes are working correctly!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "`n❌ SOME TESTS FAILED!" -ForegroundColor Red
        Write-Host "Please review the output above and fix any issues." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "`n❌ ERROR RUNNING TESTS: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
