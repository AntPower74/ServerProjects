#!/usr/bin/env python3
import os, sys, shutil, sqlite3, datetime, subprocess

HOME = "/home/antonio"
RCLONE_BIN = "/home/antonio/.local/bin/rclone"
TMP_DIR = "/tmp/db_backups"

now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d %H:%M")
date_tag = now.strftime("%Y%m%d_%H%M")

# ----------------------------------------------------
# 1. Sincronizzazione Codice su GitHub (ogni 20 min se ci sono modifiche)
# ----------------------------------------------------
def sync_git():
    try:
        status = subprocess.run(["git", "status", "--porcelain"], cwd=HOME, capture_output=True, text=True)
        if status.stdout.strip():
            print(f"[{now.isoformat()}] [GIT] Trovate modifiche, avvio commit e push...")
            subprocess.run(["git", "add", "."], cwd=HOME, check=True)
            commit_res = subprocess.run(["git", "commit", "-m", f"Auto-sync: {timestamp}"], cwd=HOME, capture_output=True, text=True)
            push_res = subprocess.run(["git", "push", "origin", "main"], cwd=HOME, capture_output=True, text=True)
            if push_res.returncode == 0:
                print(f"[{now.isoformat()}] [GIT] Push su GitHub completato con successo.")
            else:
                print(f"[{now.isoformat()}] [GIT] Errore push:\n{push_res.stderr}")
        else:
            print(f"[{now.isoformat()}] [GIT] Nessuna modifica al codice.")
    except Exception as e:
        print(f"[{now.isoformat()}] [GIT] Errore durante sync Git: {e}")

# ----------------------------------------------------
# 2. Sincronizzazione Database su Google Drive (a caldo ogni 20 min)
# ----------------------------------------------------
def safe_backup_sqlite(src_path, dst_path):
    if os.path.exists(src_path):
        try:
            src_conn = sqlite3.connect(src_path)
            dst_conn = sqlite3.connect(dst_path)
            with dst_conn:
                src_conn.backup(dst_conn)
            dst_conn.close()
            src_conn.close()
        except Exception as e:
            print(f"[{now.isoformat()}] [DB] Errore SQLite backup su {src_path}: {e}")

def sync_drive():
    try:
        os.makedirs(TMP_DIR, exist_ok=True)
        safe_backup_sqlite(os.path.join(HOME, "turni-rotazioni/data/turni.db"), os.path.join(TMP_DIR, "turni.db"))
        safe_backup_sqlite(os.path.join(HOME, "comparatore_oggetti/data/comparatore.db"), os.path.join(TMP_DIR, "comparatore.db"))
        
        fb_db = os.path.join(HOME, ".filebrowser.db")
        if os.path.exists(fb_db):
            shutil.copy2(fb_db, os.path.join(TMP_DIR, "filebrowser.db"))

        # Aggiorna sempre la versione 'latest'
        subprocess.run([RCLONE_BIN, "copy", TMP_DIR + "/", "gdrive:Backup_Server_Database/latest/"], check=True)

        # Snapshot storico salvato ogni 6 ore per non intasare Google Drive con migliaia di cartelle
        if now.minute < 20 and now.hour in [0, 6, 12, 18]:
            subprocess.run([RCLONE_BIN, "copy", TMP_DIR + "/", f"gdrive:Backup_Server_Database/history/{date_tag}/"], check=True)

        shutil.rmtree(TMP_DIR, ignore_errors=True)
        print(f"[{now.isoformat()}] [DRIVE] Database sincronizzati su Google Drive con successo.")
    except Exception as e:
        print(f"[{now.isoformat()}] [DRIVE] Errore durante sync Drive: {e}")

if __name__ == "__main__":
    sync_git()
    sync_drive()
