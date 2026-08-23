#!/usr/bin/env python3
"""
Server Web Dashboard per Ottimizzazione e Verifica Turni TPL
"""

import http.server
import socketserver
import json
import os

PORT = 8080
DIRECTORY = "/home/antonio/verifica_turni/web"

os.makedirs(DIRECTORY, exist_ok=True)

# Creiamo il file dei dati JSON per la dashboard web
with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json", "r", encoding="utf-8") as f:
    turni = json.load(f)

# Esportiamo i dati ottimizzati per il frontend
turni_ottimizzati_list = []
for t in turni:
    code = t['codice_turno']
    t_copy = dict(t)
    turni_ottimizzati_list.append(t_copy)

with open(f"{DIRECTORY}/turni_data.json", "w", encoding="utf-8") as f:
    json.dump(turni_ottimizzati_list, f, ensure_ascii=False, indent=2)

print(f"✅ Dati esportati per la dashboard web in {DIRECTORY}/turni_data.json")
