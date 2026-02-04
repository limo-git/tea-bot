# PowerShell script to update tealdr-bot on GCP VM after pushing to GitHub
# Usage: .\update-vm.ps1

Write-Host "Updating tealdr-bot on GCP VM..." -ForegroundColor Cyan

# Configuration
$INSTANCE_NAME = "tealdr-bot"
$ZONE = "us-central1-a"
$PROJECT_DIR = "tea-bot/tealdr-backend"

# Check if gcloud is installed
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] gcloud CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

Write-Host "Step 1: Pushing changes to GitHub..." -ForegroundColor Yellow
git add .
$commitMessage = Read-Host "Enter commit message (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "Update bot code"
}
git commit -m $commitMessage
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to push to GitHub!" -ForegroundColor Red
    exit 1
}

Write-Host "[SUCCESS] Pushed to GitHub!" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Connecting to VM and updating..." -ForegroundColor Yellow

# SSH command to pull, rebuild, and restart
$updateCommands = @"
cd $PROJECT_DIR && \
echo '==> Pulling latest code from GitHub...' && \
git pull origin main && \
echo '==> Stopping current bot...' && \
sudo docker stop tealdr-bot && \
sudo docker rm tealdr-bot && \
echo '==> Rebuilding Docker image...' && \
sudo docker build -t tealdr-bot . && \
echo '==> Starting bot with new code...' && \
sudo docker run -d \
    --name tealdr-bot \
    --restart unless-stopped \
    --env-file .env \
    tealdr-bot && \
echo '==> Deployment complete!' && \
echo '' && \
echo 'Bot logs (last 20 lines):' && \
sudo docker logs --tail 20 tealdr-bot
"@

gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command=$updateCommands

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Bot updated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "   Check Discord to verify bot is online" -ForegroundColor White
    Write-Host "   View full logs: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE" -ForegroundColor White
    Write-Host "                   sudo docker logs -f tealdr-bot" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERROR] Update failed!" -ForegroundColor Red
    Write-Host "SSH into VM to debug: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE" -ForegroundColor Yellow
    exit 1
}
