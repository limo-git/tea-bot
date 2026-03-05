#!/bin/bash
# Bash script to update tealdr-bot on GCP VM after pushing to GitHub
# Usage: ./update-vm.sh

set -e

echo "Updating tealdr-bot on GCP VM..."

# Configuration
INSTANCE_NAME="tealdr-bot"
ZONE="us-central1-a"
PROJECT_DIR="tea-bot/tealdr-backend"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "[ERROR] gcloud CLI not found. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "Step 1: Pushing changes to GitHub..."
git add .
read -p "Enter commit message (or press Enter for default): " commit_message
if [ -z "$commit_message" ]; then
    commit_message="Update bot code"
fi
git commit -m "$commit_message"
git push origin main

echo "[SUCCESS] Pushed to GitHub!"
echo ""

echo "Step 2: Connecting to VM and updating..."

# SSH command to pull and restart
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
cd ~/tea-bot/tealdr-backend && \
echo '==> Current commit:' && \
git log --oneline -1 && \
echo '' && \
echo '==> Pulling latest code from GitHub...' && \
git pull origin main && \
echo '' && \
echo '==> New commit:' && \
git log --oneline -1 && \
echo '' && \
echo '==> Finding Docker container...' && \
CONTAINER_ID=\$(sudo docker ps -q --filter name=tealdr) && \
if [ -z \"\$CONTAINER_ID\" ]; then \
    echo '[ERROR] No tealdr container found!' && \
    sudo docker ps -a && \
    exit 1; \
fi && \
echo \"Found container: \$CONTAINER_ID\" && \
echo '' && \
echo '==> Restarting bot...' && \
sudo docker restart \$CONTAINER_ID && \
echo '' && \
echo '==> Waiting for bot to start...' && \
sleep 3 && \
echo '' && \
echo '==> Bot logs (last 30 lines):' && \
sudo docker logs --tail 30 \$CONTAINER_ID
"

echo ""
echo "[SUCCESS] Bot updated successfully!"
echo ""
echo "Next steps:"
echo "   Check Discord to verify bot is online"
echo "   View full logs: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
echo "                   sudo docker logs -f tealdr-bot"
echo ""
