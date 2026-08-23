#!/usr/bin/env python3
import json

def parse_m(t_str):
    if not t_str: return 0
    t_clean = str(t_str).strip().replace('.', ':').replace(',', ':')
    p = t_clean.split(':')
    if len(p) == 1:
        try: return round(float(p[0]) * 60)
        except: return 0
    return int(p[0]) * 60 + int(p[1])

def fmt_time(m):
    h = (m // 60) % 24
    mins = m % 60
    return f"{h:02d}:{mins:02d}"

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] in ['Ca0080', 'To0310', 'To0330', 'To0740', 'To6030']:
        att = t['attivita']
        for a in att:
            if a.get('linea') == 'Sosta' or a.get('is_sosta_deposito'):
                p_m = parse_m(a.get('partenza'))
                a['arrivo'] = fmt_time(p_m + 30)
                a['durata_sosta_m'] = 30
                break

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ Arrivo soste aggiornato a 30m esatti!")
