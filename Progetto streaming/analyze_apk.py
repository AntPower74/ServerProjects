import sys
import re
import os

try:
    from androguard.core.apk import APK
except ImportError:
    print("Androguard not installed yet.")
    sys.exit(1)

apk_path = '/home/antonio/Progetto streaming/Vivo_Player_base.apk'
extracted_dir = '/home/antonio/Progetto streaming/extracted'

print("--- ANALISI DEI PERMESSI ---")
try:
    a = APK(apk_path)
    permissions = a.get_permissions()
    for p in permissions:
        print(p)
except Exception as e:
    print(f"Errore durante l'analisi dell'APK con androguard: {e}")

print("\n--- ANALISI DEGLI URL ---")
# Cerca nei file dex
urls = set()
url_pattern = re.compile(b'https?://[\\w./-]{5,}')

for root, _, files in os.walk(extracted_dir):
    for f in files:
        if f.endswith('.dex'):
            path = os.path.join(root, f)
            with open(path, 'rb') as dex_file:
                content = dex_file.read()
                matches = url_pattern.findall(content)
                for m in matches:
                    urls.add(m.decode('utf-8', errors='ignore'))

# Filtra alcuni url noti (google, android, w3c) per ripulire l'output
cleaned_urls = []
ignore_domains = ['schemas.android.com', 'google.com', 'w3.org', 'play.google.com', 'apache.org']

for u in urls:
    if not any(d in u for d in ignore_domains):
        cleaned_urls.append(u)

cleaned_urls.sort()
for u in cleaned_urls:
    print(u)
