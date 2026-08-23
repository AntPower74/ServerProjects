#!/usr/bin/env python3
import json

DEPOSITO_MAP = {
    'To': 'Torino',
    'Pi': 'Pinerolo',
    'Pe': 'Perosa Argentina',
    'Pt': 'Pont Saint Martin',
    'Su': 'Susa',
    'Pb': 'Piobesi',
    'Ca': 'Caselle',
    'Sa': 'Salbertrand',
    'Lu': 'Luserna San Giovanni',
    'Ba': 'Barge',
    'Iv': 'Ivrea',
    'Bo': 'Bobbio Pellice',
    'FT': 'Fuori Turno'
}

for path in [
    "/home/antonio/verifica_turni/web/turni_data.json",
    "/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json"
]:
    with open(path, "r", encoding="utf-8") as f:
        turni = json.load(f)

    for t in turni:
        code = t['codice_turno']
        pref = code[:2]
        if pref in DEPOSITO_MAP:
            t['deposito'] = DEPOSITO_MAP[pref]
            if pref == 'FT':
                t['nome_turno'] = f"FUORI TURNO {code[2:]}"
            elif pref == 'Pb' and t['nome_turno'] == code:
                t['nome_turno'] = f"TURNO {code[2:]} DI PIOBESI"
            elif pref == 'Pt' and t['nome_turno'] == code:
                t['nome_turno'] = f"TURNO {code[2:]} DI PONT ST MARTIN"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ Anagrafica depositi aggiornata con massima precisione!")
