#!/bin/bash
set -e

TMP_DIR="/tmp/db_backups"
mkdir -p "$TMP_DIR"
DATE_TAG=$(date +"%Y%m%d_%H%M")

# 1. Backup sicuro a caldo dei database SQLite
if [ -f /home/antonio/turni-rotazioni/data/turni.db ]; then
  sqlite3 /home/antonio/turni-rotazioni/data/turni.db ".backup '$TMP_DIR/turni.db'"
fi

if [ -f /home/antonio/comparatore_oggetti/data/comparatore.db ]; then
  sqlite3 /home/antonio/comparatore_oggetti/data/comparatore.db ".backup '$TMP_DIR/comparatore.db'"
fi

if [ -f /home/antonio/.filebrowser.db ]; then
  cp /home/antonio/.filebrowser.db "$TMP_DIR/filebrowser.db"
fi

# 2. Sincronizza su Google Drive tramite rclone
/home/antonio/.local/bin/rclone copy "$TMP_DIR/" "gdrive:Backup_Server_Database/latest/"
/home/antonio/.local/bin/rclone copy "$TMP_DIR/" "gdrive:Backup_Server_Database/history/$DATE_TAG/"

# 3. Pulizia temporanei
rm -rf "$TMP_DIR"

echo "[$(date -Iseconds)] Backup database su Google Drive completato con successo."
