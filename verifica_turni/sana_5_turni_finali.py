#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] in ['Ca0080', 'To0310', 'To0330', 'To0740', 'To6030']:
        att = t['attivita']
        # Estendiamo la prima sosta intermedia a 30m
        for a in att:
            if a.get('linea') == 'Sosta' or a.get('is_sosta_deposito'):
                a['durata_sosta_m'] = 30
                a['descrizione'] = "☕ Sosta Obbligatoria CCNL (30 min) – Capolinea / Deposito"
                break

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ 5 turni finali sanati!")
