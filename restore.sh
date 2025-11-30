#!/bin/bash
# Restore script for Local Host Dashboard

BACKUP_DIR="/home/pi/backup-dashboard"
TARGET_DIR="/home/pi/Local-Host-Dashboard"

# Use "latest" backup if no argument provided, otherwise use the specified backup
RESTORE_FROM="${1:-${BACKUP_DIR}/latest}"

if [ ! -d "$RESTORE_FROM" ]; then
    echo "❌ Error: Backup directory not found: $RESTORE_FROM"
    echo ""
    echo "Available backups:"
    ls -d "$BACKUP_DIR"/dashboard_backup_* 2>/dev/null | tail -10
    exit 1
fi

echo "Restoring from: $RESTORE_FROM"
echo ""
echo "⚠️  This will overwrite your current dashboard application!"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Stop the dashboard service
echo "Stopping dashboard service..."
sudo systemctl stop dashboard

# Backup current version before restoring
echo "Creating safety backup of current version..."
SAFETY_BACKUP="${TARGET_DIR}/backup_before_restore_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$SAFETY_BACKUP"
cp -r "$TARGET_DIR"/app "$SAFETY_BACKUP/" 2>/dev/null || true
cp -r "$TARGET_DIR"/templates "$SAFETY_BACKUP/" 2>/dev/null || true
cp -r "$TARGET_DIR"/static "$SAFETY_BACKUP/" 2>/dev/null || true
echo "Safety backup saved to: $SAFETY_BACKUP"

# Restore files
echo "Restoring application files..."
cp -r "$RESTORE_FROM"/app "$TARGET_DIR/"
cp -r "$RESTORE_FROM"/templates "$TARGET_DIR/"
cp -r "$RESTORE_FROM"/static "$TARGET_DIR/"
cp "$RESTORE_FROM"/run.py "$TARGET_DIR/"
cp "$RESTORE_FROM"/requirements.txt "$TARGET_DIR/"
cp "$RESTORE_FROM"/setup.sh "$TARGET_DIR/"

# Reinstall Python dependencies
echo "Reinstalling Python dependencies..."
cd "$TARGET_DIR"
source venv/bin/activate
pip install -q -r requirements.txt

# Start the dashboard service
echo "Starting dashboard service..."
sudo systemctl start dashboard

sleep 2

# Verify service is running
if sudo systemctl is-active --quiet dashboard; then
    echo "✓ Restore completed successfully!"
    echo "✓ Dashboard service is running"
    echo ""
    echo "Access the dashboard at:"
    echo "http://$(hostname -I | awk '{print $1}'):5002"
else
    echo "❌ Error: Dashboard service failed to start"
    echo "Check logs with: sudo journalctl -u dashboard -f"
    exit 1
fi
