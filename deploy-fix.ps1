# Quick deployment script for user mention filtering fix
# Run this to deploy the fix to the VM

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploying User Mention Filtering Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This will:" -ForegroundColor Yellow
Write-Host "  1. SSH into your VM" -ForegroundColor White
Write-Host "  2. Pull latest code from GitHub" -ForegroundColor White
Write-Host "  3. Restart the bot" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Continue? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Deployment cancelled" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Step 1: SSH into VM and pull latest code..." -ForegroundColor Yellow

# Create a script to run on the VM
$vmScript = @"
cd ~/tea-bot/tealdr-backend
echo "Current commit:"
git log --oneline -1
echo ""
echo "Pulling latest changes..."
git pull origin main
echo ""
echo "New commit:"
git log --oneline -1
echo ""
echo "Restarting bot..."
sudo docker-compose restart
echo ""
echo "Deployment complete!"
"@

# Save to temp file
$vmScript | Out-File -FilePath "temp_deploy.sh" -Encoding UTF8

Write-Host "Executing deployment on VM..." -ForegroundColor Yellow
gcloud compute ssh tealdr-bot --zone=us-central1-a --command="bash -s" < temp_deploy.sh

# Clean up
Remove-Item "temp_deploy.sh"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "The bot should now correctly handle user mention queries." -ForegroundColor Cyan
Write-Host ""
Write-Host "Test with:" -ForegroundColor Yellow
Write-Host "  /ask query:what @user is trying to convey" -ForegroundColor White
Write-Host ""
Write-Host "Expected behavior:" -ForegroundColor Yellow
Write-Host "  - Intent: user_messages (not summarization)" -ForegroundColor Green
Write-Host "  - Results: Only messages FROM that user" -ForegroundColor Green
