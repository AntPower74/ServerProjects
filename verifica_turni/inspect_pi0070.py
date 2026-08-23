#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    orig = json.load(f)

for t in orig:
    if t['codice_turno'] == 'Pi0070':
        print(json.dumps(t, indent=2))
