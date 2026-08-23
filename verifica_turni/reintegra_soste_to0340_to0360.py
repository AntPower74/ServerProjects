#!/usr/bin/env python3
import json

def parse_m(t_str):
    p = str(t_str).replace('.', ':').split(':')
    return int(p[0]) * 60 + int(p[1])

def fmt_time(m):
    h = (m // 60) % 24
    mins = m % 60
    return f"{h:02d}:{mins:02d}"

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] in ['To0340', 'To0360']:
        att = t['attivita']
        nuova = []
        for i in range(len(att)):
            nuova.append(att[i])
            if i < len(att) - 1:
                arr_i = parse_m(att[i].get('arrivo'))
                part_next = parse_m(att[next_i := i+1].get('partenza'))
                gap = part_next - arr_i if part_next >= arr_i else (1440 - arr_i + part_next)
                if gap >= 15:
                    loc = att[i].get('a') or 'Deposito'
                    nuova.append({
                        'linea': 'Sosta',
                        'descrizione': f"☕ Sosta Obbligatoria CCNL / Pausa ({gap}m) – {loc}",
                        'da': loc,
                        'a': loc,
                        'partenza': fmt_time(arr_i),
                        'arrivo': fmt_time(part_next),
                        'km': '-',
                        'durata_sosta_m': gap,
                        'is_sosta_deposito': True
                    })
        t['attivita'] = nuova

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ Soste reinserite nei gap naturali di To0340 e To0360!")
