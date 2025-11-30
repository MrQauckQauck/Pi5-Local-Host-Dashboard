#!/bin/bash
# Backup script for Local Host Dashboard

BACKUP_DIR="/home/pi/backup-dashboard"
SOURCE_DIR="/home/pi/Local-Host-Dashboard"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="dashboard_backup_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create timestamped backup
echo "Creating backup at: $BACKUP_PATH"
mkdir -p "$BACKUP_PATH"

# Copy application files (excluding venv and __pycache__)
cp -r "$SOURCE_DIR/app" "$BACKUP_PATH/"
cp -r "$SOURCE_DIR/templates" "$BACKUP_PATH/"
cp -r "$SOURCE_DIR/static" "$BACKUP_PATH/"
cp "$SOURCE_DIR/run.py" "$BACKUP_PATH/"
cp "$SOURCE_DIR/requirements.txt" "$BACKUP_PATH/"
cp "$SOURCE_DIR/setup.sh" "$BACKUP_PATH/"
cp "$SOURCE_DIR/dashboard.service" "$BACKUP_PATH/"
cp "$SOURCE_DIR/README.md" "$BACKUP_PATH/" 2>/dev/null || true

# Create a backup info file
cat > "$BACKUP_PATH/BACKUP_INFO.txt" << EOF
Local Host Dashboard Backup
Created: $(date)
Hostname: $(hostname)
IP Address: $(hostname -I)
Backup Path: $BACKUP_PATH

Contents:
- app/ - Flask application code
- templates/ - HTML templates
- static/ - CSS and JavaScript files
- run.py - Main application entry point
- requirements.txt - Python dependencies
- setup.sh - Setup script
- dashboard.service - Systemd service file
- README.md - Documentation

To restore this backup:
1. Navigate to the backup directory
2. Copy all files back to /home/pi/Local-Host-Dashboard/
3. Run: cd /home/pi/Local-Host-Dashboard && source venv/bin/activate && pip install -r requirements.txt
4. Restart the service: sudo systemctl restart dashboard
EOF

echo "✓ Backup completed successfully!"
echo "Backup location: $BACKUP_PATH"

# Keep only last 5 backups to save space
cd "$BACKUP_DIR"
ls -t -d dashboard_backup_* 2>/dev/null | tail -n +6 | xargs -r rm -rf

echo "✓ Cleanup completed (kept last 5 backups)"

# Create a symlink to the latest backup
ln -sf "$BACKUP_NAME" "$BACKUP_DIR/latest"
echo "Latest backup symlink updated"
