#!/bin/bash
echo "Starting Subconscious Brain Sync..."
rsync -avz -e "ssh -o StrictHostKeyChecking=no" root@2.24.83.231:/docker/openclaw-xlgf/data/backups/ /home/fq9f/acutis_backups/
find /home/fq9f/acutis_backups/ -name "Acutis_backup_*.tar.gz" -type f -mtime +60 -exec rm {} \;
echo "Sync complete and old memories pruned."
