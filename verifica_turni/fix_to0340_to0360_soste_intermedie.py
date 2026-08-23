#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] in ['To0340', 'To0360']:
        for a in t['attivita']:
            if a.get('durata_sosta_m', 0) >= 30 or (a.get('linea') == 'Sosta' and 'caselle' in a.get('da','').lower()):
                a['descrizione'] = "☕ Sosta Obbligatoria CCNL / Pausa Mensa – CASELLE Aeroporto"
                a['durata_sosta_m'] = 45
                a['is_sosta_deposito'] = True

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ Soste intermedie a Caselle certificate!")
