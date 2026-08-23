#!/usr/bin/env python3
import json

for path in [
    "/home/antonio/verifica_turni/web/turni_data.json",
    "/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json"
]:
    with open(path, "r", encoding="utf-8") as f:
        turni = json.load(f)

    for t in turni:
        if t['codice_turno'].startswith('Ca'):
            t['deposito'] = "Caselle"
            if t['nome_turno'] == t['codice_turno']:
                t['nome_turno'] = f"TURNO {t['codice_turno'][2:]} DI CASELLE"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ Deposito per i turni 'Ca' aggiornato a 'Caselle' nei file JSON.")
