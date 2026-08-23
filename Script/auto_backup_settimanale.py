#!/usr/bin/env python3
# ==============================================================================
# SCRIPT DI BACKUP SETTIMANALE AUTOMATICO - ANTONIO
# ==============================================================================
import os, sys, shutil, stat, tarfile, zipfile, time, datetime, glob

HOME = "/home/antonio"
BACKUPS_DIR = os.path.join(HOME, "backups")
SINGOLI_DIR = os.path.join(BACKUPS_DIR, "singoli_progetti")
ARCHIVE_DIR = os.path.join(BACKUPS_DIR, "archivio_storico")
STAGING_DIR = os.path.join(BACKUPS_DIR, "staging_auto")

os.makedirs(SINGOLI_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

DATE_STR = datetime.datetime.now().strftime("%Y%m%d_%H%M")
print(f"[{datetime.datetime.now().isoformat()}] === INIZIO BACKUP SETTIMANALE PROGETTI ===")

EXCLUDE_DIRS = {
    "node_modules", "venv", ".cache", ".npm", ".gradle",
    "android-sdk", "jdk-17.0.2", "jdk-21.0.2",
    "node-v20.12.2-linux-x64", "node-v22.2.0-linux-x64",
    ".gemini", ".claude", ".npm-global", "__pycache__",
    "staging", "backups", "staging_auto"
}
EXCLUDE_EXTS = {".tar.gz.1", ".tar.gz.2", ".tar.xz.1", ".tar.xz.2", ".log", ".sock", ".pid"}

# 1. Genera ZIP singoli per ciascun progetto
projects = [
    ("SmartTurnoArriva", "SmartTurnoArriva.zip"),
    ("comparatore_oggetti", "Prezzly_Comparatore.zip"),
    ("turni-rotazioni", "Turni_Rotazioni.zip"),
    ("sitoofferte", "Sito_Offerte_e_Bot.zip"),
    ("streampro-backend", "StreamPRO_Backend.zip"),
    ("Progetto streaming", "StreamPRO_App_Android.zip"),
    ("streampro_releases", "StreamPRO_Releases.zip"),
    ("streampro_static", "StreamPRO_Static.zip"),
    ("TplPiemonteNews", "TplPiemonteNews.zip"),
    ("arriva_move", "Arriva_Move.zip"),
    ("Percorsi", "Percorsi_GPX.zip"),
    ("verifica_turni", "Verifica_Turni.zip"),
    ("Script", "Script_e_Utility.zip"),
    ("sito", "Sito.zip")
]

print("1. Aggiornamento ZIP singoli progetti...")
for folder, zip_name in projects:
    src_dir = os.path.join(HOME, folder)
    if os.path.exists(src_dir):
        out_path = os.path.join(SINGOLI_DIR, zip_name)
        with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for root, dirs, files in os.walk(src_dir):
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                for file in files:
                    if any(file.endswith(ext) for ext in EXCLUDE_EXTS) and file != "update-manifest.json":
                        continue
                    full_fp = os.path.join(root, file)
                    rel_fp = os.path.relpath(full_fp, HOME)
                    try:
                        zf.write(full_fp, rel_fp)
                    except Exception:
                        pass

# Keystore
ks_src = os.path.join(BACKUPS_DIR, "smartturnoarriva-signing")
if os.path.exists(ks_src):
    with zipfile.ZipFile(os.path.join(SINGOLI_DIR, "SmartTurnoArriva_Keystore_Firma.zip"), "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in os.listdir(ks_src):
            fp = os.path.join(ks_src, f)
            if os.path.isfile(fp):
                zf.write(fp, f)

# Nginx config
with zipfile.ZipFile(os.path.join(SINGOLI_DIR, "Nginx_e_Configurazioni_Server.zip"), "w", compression=zipfile.ZIP_DEFLATED) as zf:
    sites_dir = "/etc/nginx/sites-available"
    if os.path.exists(sites_dir):
        for s in os.listdir(sites_dir):
            sp = os.path.join(sites_dir, s)
            if os.path.isfile(sp):
                zf.write(sp, os.path.join("nginx_sites", s))
    if os.path.exists(os.path.join(HOME, ".filebrowser.db")):
        zf.write(os.path.join(HOME, ".filebrowser.db"), "filebrowser.db")

print("2. Creazione PROGETTI_ZIP_SEPARATI.zip...")
master_zip = os.path.join(HOME, "PROGETTI_ZIP_SEPARATI.zip")
with zipfile.ZipFile(master_zip, "w", compression=zipfile.ZIP_STORED) as mzf:
    for item in sorted(os.listdir(SINGOLI_DIR)):
        if item.endswith(".zip"):
            fp = os.path.join(SINGOLI_DIR, item)
            mzf.write(fp, os.path.join("progetti_singoli_zip", item))

# 3. Aggiorna archivio autoinstallante completo
print("3. Aggiornamento backup_server_antonio.zip autoinstallante...")
# Crea staging temporaneo per l'autoinstallante
if os.path.exists(STAGING_DIR):
    shutil.rmtree(STAGING_DIR)
os.makedirs(os.path.join(STAGING_DIR, "projects"), exist_ok=True)
os.makedirs(os.path.join(STAGING_DIR, "nginx/sites-available"), exist_ok=True)
os.makedirs(os.path.join(STAGING_DIR, "var_www/streampro"), exist_ok=True)

# Copia script installatori
for s_file in ["restore.sh", "restore_linux.sh", "restore_windows.bat", "restore_windows.ps1", "start_all_windows.bat", "stop_all_windows.bat", "ecosystem.windows.config.js", "ecosystem.config.js", "GUIDA_RIPRISTINO.md", "README.md", "crontab.txt"]:
    src_f = os.path.join(HOME, s_file)
    if not os.path.exists(src_f):
        src_f = os.path.join(HOME, "backups", s_file)
    if os.path.exists(src_f):
        shutil.copy2(src_f, os.path.join(STAGING_DIR, s_file))

# Copia cartelle progetti
for folder, _ in projects:
    s = os.path.join(HOME, folder)
    t = os.path.join(STAGING_DIR, "projects", folder)
    if os.path.exists(s):
        def _ignore(directory, contents):
            ignored = set()
            for c in contents:
                full = os.path.join(directory, c)
                try:
                    mode = os.stat(full, follow_symlinks=False).st_mode
                    if stat.S_ISSOCK(mode) or stat.S_ISFIFO(mode):
                        ignored.add(c)
                        continue
                except Exception:
                    pass
                if os.path.isdir(full) and c in EXCLUDE_DIRS:
                    ignored.add(c)
                elif any(c.endswith(ext) for ext in EXCLUDE_EXTS) and c != "update-manifest.json":
                    ignored.add(c)
            return ignored
        shutil.copytree(s, t, ignore=_ignore, symlinks=True)

# Copia file root e configurazioni
for rf in [".filebrowser.db", ".bashrc", ".profile", "separazione_utenti.sh", "setup_files_antonio.sh"]:
    fp = os.path.join(HOME, rf)
    if os.path.exists(fp):
        shutil.copy2(fp, os.path.join(STAGING_DIR, "projects", rf))

# Nginx e var_www
if os.path.exists("/etc/nginx/sites-available"):
    for sf in os.listdir("/etc/nginx/sites-available"):
        sp = os.path.join("/etc/nginx/sites-available", sf)
        if os.path.isfile(sp):
            shutil.copy2(sp, os.path.join(STAGING_DIR, "nginx/sites-available", sf))

if os.path.exists("/var/www/streampro"):
    shutil.copytree("/var/www/streampro", os.path.join(STAGING_DIR, "var_www/streampro"), dirs_exist_ok=True)

# Crea tar.gz e zip autoinstallanti
full_tar = os.path.join(HOME, "backup_server_antonio.tar.gz")
with tarfile.open(full_tar, "w:gz") as tar:
    tar.add(STAGING_DIR, arcname="backup_antonio_bundle")

full_zip = os.path.join(HOME, "backup_server_antonio.zip")
with tarfile.open(full_tar, "r:gz") as tar:
    with zipfile.ZipFile(full_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for member in tar.getmembers():
            if member.isdir():
                zinfo = zipfile.ZipInfo(member.name + "/")
                zinfo.date_time = time.localtime(member.mtime)[:6]
                zipf.writestr(zinfo, "")
            elif member.isreg():
                f = tar.extractfile(member)
                if f is not None:
                    zinfo = zipfile.ZipInfo(member.name)
                    zinfo.date_time = time.localtime(member.mtime)[:6]
                    zinfo.file_size = member.size
                    zinfo.external_attr = (member.mode & 0xFFFF) << 16
                    zipf.writestr(zinfo, f.read())

shutil.rmtree(STAGING_DIR, ignore_errors=True)

# Copia datata nello storico
shutil.copy2(master_zip, os.path.join(ARCHIVE_DIR, f"PROGETTI_ZIP_SEPARATI_{DATE_STR}.zip"))

# Pulisci backup storici più vecchi di 15 giorni per preservare spazio disco
now = time.time()
for old_file in glob.glob(os.path.join(ARCHIVE_DIR, "*.zip")) + glob.glob(os.path.join(ARCHIVE_DIR, "*.tar.gz")):
    if os.stat(old_file).st_mtime < now - (15 * 86400):
        try:
            os.remove(old_file)
            print(f"Rimosso vecchio backup: {old_file}")
        except Exception:
            pass

print(f"[{datetime.datetime.now().isoformat()}] === BACKUP SETTIMANALE COMPLETATO CON SUCCESSO! ===")
