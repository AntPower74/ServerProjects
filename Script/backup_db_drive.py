#!/usr/bin/env python3
import os, sys, shutil, sqlite3, datetime, subprocess

HOME = "/home/antonio"
TMP_DIR = "/tmp/db_backups"
RCLONE_BIN = "/home/antonio/.local/bin/rclone"

os.makedirs(TMP_DIR, exist_ok=True)
date_tag = datetime.datetime.now().strftime("%Y%m%d_%H%M")

def safe_backup_sqlite(src_path, dst_path):
    if os.path.exists(src_path):
        try:
            src_conn = sqlite3.connect(src_path)
            dst_conn = sqlite3.connect(dst_path)
            with dst_conn:
                src_conn.backup(dst_conn)
            dst_conn.close()
            src_conn.close()
            print(f"Backed up SQLite: {src_path} -> {dst_path}")
        except Exception as e:
            print(f"Error backing up {src_path}: {e}")

# 1. Backup sicuro a caldo dei database SQLite
safe_backup_sqlite(os.path.join(HOME, "turni-rotazioni/data/turni.db"), os.path.join(TMP_DIR, "turni.db"))
safe_backup_sqlite(os.path.join(HOME, "comparatore_oggetti/data/comparatore.db"), os.path.join(TMP_DIR, "comparatore.db"))

fb_db = os.path.join(HOME, ".filebrowser.db")
if os.path.exists(fb_db):
    shutil.copy2(fb_db, os.path.join(TMP_DIR, "filebrowser.db"))

# 2. Upload su Google Drive con rclone
cmd_latest = [RCLONE_BIN, "copy", TMP_DIR + "/", "gdrive:Backup_Server_Database/latest/"]
cmd_history = [RCLONE_BIN, "copy", TMP_DIR + "/", f"gdrive:Backup_Server_Database/history/{date_tag}/"]

subprocess.run(cmd_latest, check=True)
subprocess.run(cmd_history, check=True)

# 3. Pulizia temporanei
shutil.rmtree(TMP_DIR, ignore_errors=True)
print(f"[{datetime.datetime.now().isoformat()}] Backup database su Google Drive completato con successo.")

