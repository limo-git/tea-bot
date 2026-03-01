# PowerShell script to run all Temporal Graph RAG tests

Write-Host "🧪 Temporal Graph RAG Test Suite" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Set up environment
$env:PYTHONPATH = "$PWD"

# Function to run a test and capture results
function Run-Test {
    param(
        [string]$TestName,
        [string]$TestScript
    )
    
    Write-Host "`n🔍 Running $TestName..." -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Gray
    
    try {
        python $TestScript
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $TestName - PASSED" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ $TestName - FAILED (Exit code: $LASTEXITCODE)" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ $TestName - ERROR: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Change to tests directory
Set-Location tests

$passedTests = 0
$totalTests = 0

# Run unit tests
$totalTests++
if (Run-Test "Unit Tests" "run_all_tests.py") {
    $passedTests++
}

# Run deployment verification
$totalTests++
if (Run-Test "Deployment Verification" "test_deployment.py") {
    $passedTests++
}

# Print final summary
Write-Host "`n" -NoNewline
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "📊 FINAL TEST SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "Total Test Suites: $totalTests"
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $($totalTests - $passedTests)" -ForegroundColor Red

$successRate = if ($totalTests -gt 0) { ($passedTests / $totalTests * 100) } else { 0 }
Write-Host "Success Rate: $($successRate.ToString('F1'))%"

if ($passedTests -eq $totalTests) {
    Write-Host "`n🎉 ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "Your Temporal Graph RAG system is working perfectly!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠️ SOME TESTS FAILED!" -ForegroundColor Red
    Write-Host "Please review the output above and fix any issues." -ForegroundColor Red
    exit 1
}
