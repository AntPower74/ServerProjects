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

def fmt_durata(m):
    if not m or m < 0: return "0h 00m"
    h = m // 60
    mins = m % 60
    return f"{h}h {mins:02d}m"

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni_reali = json.load(f)
reali_map = {t['codice_turno']: t for t in turni_reali}

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni_opt = json.load(f)

for t in turni_opt:
    code = t['codice_turno']
    if code in ['Ba3510', 'Ca0070', 'Pe0240', 'To0340', 'To0350', 'To0360', 'To0640', 'To0660', 'To0680']:
        orig = reali_map[code]
        in_m = parse_m(orig['inizio_servizio'])
        fin_m = parse_m(orig['fine_servizio'])
        dep = orig.get('deposito', 'Torino')
        
        # Prendiamo le attività dall'originale escludendo lo stacco passivo di 15h
        att_raw = [a for a in orig['attivita'] if not (a.get('linea') == 'Sosta' and a.get('durata_sosta_m', 0) >= 600)]
        
        # Ordiniamo con chiave continua dal pomeriggio (in_m) in poi
        def time_key(a):
            p = parse_m(a.get('partenza'))
            return p if p >= in_m else p + 1440
            
        att_sorted = sorted(att_raw, key=time_key)
        
        # Filtriamo corse per un turno continuo da ~6h30 / 7h00
        nastro_target = 420 # 7h00
        timeline = []
        curr_m = in_m
        
        for a in att_sorted:
            p_m = parse_m(a.get('partenza'))
            arr_m = parse_m(a.get('arrivo'))
            delta_p = p_m - in_m if p_m >= in_m else (1440 - in_m + p_m)
            
            if delta_p <= nastro_target - 30:
                timeline.append(a)
                curr_m = arr_m if arr_m >= in_m else arr_m + 1440
                
        # Sosta certificata 30m al termine o intermedia
        has_30m = any((a.get('linea') == 'Sosta' or a.get('is_sosta_deposito')) and a.get('durata_sosta_m', 0) >= 30 for a in timeline)
        if not has_30m:
            timeline.append({
                'linea': 'Sosta',
                'descrizione': f"☕ Sosta Obbligatoria CCNL (30 min) – {dep} Deposito",
                'da': f"{dep} Deposito",
                'a': f"{dep} Deposito",
                'partenza': fmt_time(curr_m),
                'arrivo': fmt_time(curr_m + 30),
                'km': '-',
                'durata_sosta_m': 30,
                'is_sosta_deposito': True
            })
            curr_m += 30
            
        # Chiusura
        timeline.append({
            'linea': 'Disp',
            'descrizione': f"Rientro deposito e chiusura turno continuo – {dep} Deposito",
            'da': f"{dep} Deposito",
            'a': f"{dep} Deposito",
            'partenza': fmt_time(curr_m),
            'arrivo': fmt_time(curr_m + 10),
            'km': '-'
        })
        fin_eff_m = (curr_m + 10) % 1440
        
        n_m = (curr_m + 10) - in_m
        t['inizio_servizio'] = orig['inizio_servizio']
        t['fine_servizio'] = fmt_time(fin_eff_m)
        t['nastro'] = f"{n_m/60:.2f}"
        t['nastro_str'] = fmt_durata(n_m)
        t['nastro_m'] = n_m
        t['ore_lavoro'] = f"{n_m/60:.2f}"
        t['olg_str'] = fmt_durata(n_m)
        t['olg_m'] = n_m
        t['attivita'] = timeline

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni_opt, f, ensure_ascii=False, indent=2)

print("✅ 9 turni serali ricostruiti con corse reali!")
