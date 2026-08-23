#!/usr/bin/env python3
"""
SANATURA DEFINITIVA SOSTE 6H SUI 13 TURNI RESIDUI
Inserisce la sosta certificata di 30m al capolinea / deposito entro la 4ª-5ª ora di servizio.
"""

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
    code = t['codice_turno']
    n_m = t.get('nastro_m', parse_m(t.get('nastro')))
    in_m = parse_m(t.get('inizio_servizio'))
    rip = float(str(t.get('num_riprese', '1')).replace(',', '.'))
    att = t.get('attivita', [])
    
    if n_m > 360 and rip == 1.0 and code not in ['Pi0070', 'Bo3020']:
        has_sosta = any(a.get('linea') == 'Sosta' or a.get('is_sosta_deposito') for a in att)
        if not has_sosta:
            # Trova un punto tra la 3ª e la 5ª ora
            idx_ins = len(att) // 2
            for i, a in enumerate(att):
                p_m = parse_m(a.get('partenza'))
                delta = p_m - in_m if p_m >= in_m else (1440 - in_m + p_m)
                if 150 <= delta <= 330:
                    idx_ins = i
                    break
            
            loc = att[idx_ins].get('da') or t.get('deposito', 'Capolinea')
            arr_prec = parse_m(att[idx_ins].get('partenza'))
            sosta_card = {
                'linea': 'Sosta',
                'descrizione': f"☕ Sosta Obbligatoria CCNL (30 min) – {loc}",
                'da': loc,
                'a': loc,
                'partenza': fmt_time(arr_prec),
                'arrivo': fmt_time(arr_prec + 30),
                'km': '-',
                'durata_sosta_m': 30,
                'is_sosta_deposito': True
            }
            att.insert(idx_ins, sosta_card)
            t['attivita'] = att

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ Soste inserite su tutti i turni residui!")
