#!/bin/bash
# Odoo Backup Script
# Run daily via cron

set -e

BACKUP_DIR=~/odoo/backups
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

echo "Starting Odoo backup at $(date)"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
echo "Backing up database..."
docker exec odoo-db pg_dump -U odoo odoo_db > "$BACKUP_DIR/db_$DATE.sql"

# Backup filestore
echo "Backing up filestore..."
tar -czf "$BACKUP_DIR/files_$DATE.tar.gz" ~/odoo/data

# Compress database backup
echo "Compressing database backup..."
gzip "$BACKUP_DIR/db_$DATE.sql"

# Clean old backups
echo "Cleaning backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "files_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# List current backups
echo "Current backups:"
ls -lh "$BACKUP_DIR"

echo "Backup completed successfully at $(date)"
