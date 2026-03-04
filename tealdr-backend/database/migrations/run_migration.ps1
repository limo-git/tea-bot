# PowerShell script to run database migrations
# Usage: .\run_migration.ps1 -MigrationFile "001_add_bm25_support.sql"

param(
    [Parameter(Mandatory=$true)]
    [string]$MigrationFile
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running Database Migration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Load environment variables
if (Test-Path ".env") {
    Write-Host "Loading environment variables from .env..." -ForegroundColor Yellow
    Get-Content .env | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

$SUPABASE_URL = $env:SUPABASE_URL
$SUPABASE_KEY = $env:SUPABASE_KEY

if (-not $SUPABASE_URL -or -not $SUPABASE_KEY) {
    Write-Host "ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env" -ForegroundColor Red
    exit 1
}

# Extract project ID from Supabase URL
$SUPABASE_PROJECT_ID = ($SUPABASE_URL -replace 'https://([^.]+)\.supabase\.co', '$1')

Write-Host "Supabase Project: $SUPABASE_PROJECT_ID" -ForegroundColor Green
Write-Host "Migration File: $MigrationFile" -ForegroundColor Green
Write-Host ""

# Check if migration file exists
$migrationPath = "database\migrations\$MigrationFile"
if (-not (Test-Path $migrationPath)) {
    Write-Host "ERROR: Migration file not found: $migrationPath" -ForegroundColor Red
    exit 1
}

Write-Host "Reading migration SQL..." -ForegroundColor Yellow
$sql = Get-Content $migrationPath -Raw

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "MIGRATION SQL:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host $sql
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

$confirmation = Read-Host "Do you want to execute this migration? (yes/no)"
if ($confirmation -ne "yes") {
    Write-Host "Migration cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Executing migration via Supabase REST API..." -ForegroundColor Yellow

# Note: Supabase doesn't have a direct SQL execution endpoint via REST API
# You need to use the Supabase CLI or connect directly to PostgreSQL
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MANUAL EXECUTION REQUIRED" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To execute this migration, you have two options:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Option 1: Supabase Dashboard (Recommended)" -ForegroundColor Green
Write-Host "  1. Go to: https://supabase.com/dashboard/project/$SUPABASE_PROJECT_ID/sql/new" -ForegroundColor White
Write-Host "  2. Copy the SQL from: $migrationPath" -ForegroundColor White
Write-Host "  3. Paste and execute in the SQL Editor" -ForegroundColor White
Write-Host ""
Write-Host "Option 2: Supabase CLI" -ForegroundColor Green
Write-Host "  supabase db execute --file $migrationPath --project-ref $SUPABASE_PROJECT_ID" -ForegroundColor White
Write-Host ""
Write-Host "Option 3: Direct PostgreSQL Connection" -ForegroundColor Green
Write-Host "  psql -h db.$SUPABASE_PROJECT_ID.supabase.co -U postgres -d postgres -f $migrationPath" -ForegroundColor White
Write-Host ""
