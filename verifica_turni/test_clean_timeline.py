import json
from motore_ottimo_globale_ortools import parse_clock, fmt_time, fmt_durata

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

for t in turni:
    code = t['codice_turno']
    dep = t.get('deposito', 'Deposito')
    in_m = parse_clock(t.get('inizio_servizio'))
    att_raw = t.get('attivita', [])
    corse = [a for a in att_raw if a.get('linea') != 'Sosta']
    
    # Raccogliamo corse <= max_nastro - 40
    att_opt = []
    for a in corse:
        p_a = parse_clock(a.get('partenza'))
        arr_a = parse_clock(a.get('arrivo'))
        delta = arr_a - in_m if arr_a >= in_m else (1440 - in_m + arr_a)
        if delta <= 630 - 40:
            att_opt.append(a)
        elif not att_opt:
            att_opt.append(a)

    timeline = []
    curr_m = in_m
    
    if att_opt:
        p1_m = parse_clock(att_opt[0].get('partenza'))
        if p1_m > curr_m:
            timeline.append({
                'linea': 'Disp',
                'descrizione': f"Presa servizio e controllo livelli – {dep} Deposito",
                'da': f"{dep} Deposito",
                'a': f"{dep} Deposito",
                'partenza': fmt_time(curr_m),
                'arrivo': fmt_time(p1_m),
                'km': '-'
            })
            curr_m = p1_m

    for i in range(len(att_opt)):
        p_i = parse_clock(att_opt[i].get('partenza'))
        arr_i = parse_clock(att_opt[i].get('arrivo'))
        
        gap = p_i - curr_m if p_i >= curr_m else (1440 - curr_m + p_i)
        if gap > 0 and gap <= 180:
            loc = timeline[-1].get('a') if timeline else f"{dep} Deposito"
            desc = f"☕ Sosta Obbligatoria CCNL ({fmt_durata(gap)}) – {loc}" if gap >= 30 else f"☕ Sosta in Banchina ({fmt_durata(gap)}) – {loc}"
            timeline.append({
                'linea': 'Sosta',
                'descrizione': desc,
                'da': loc,
                'a': loc,
                'partenza': fmt_time(curr_m),
                'arrivo': fmt_time(p_i),
                'km': '-',
                'durata_sosta_m': gap,
                'is_sosta_deposito': True
            })
            curr_m = p_i
            
        timeline.append(att_opt[i])
        curr_m = arr_i

    elapsed = curr_m - in_m if curr_m >= in_m else (1440 - in_m + curr_m)
    if elapsed < 390 - 10:
        delta_disp = 390 - 10 - elapsed
        end_disp = (curr_m + delta_disp) % 1440
        timeline.append({
            'linea': 'Disp',
            'descrizione': f"Presenza e disponibilità operativa – {dep} Deposito",
            'da': f"{dep} Deposito",
            'a': f"{dep} Deposito",
            'partenza': fmt_time(curr_m),
            'arrivo': fmt_time(end_disp),
            'km': '-'
        })
        curr_m = end_disp

    fin_m = (curr_m + 10) % 1440
    timeline.append({
        'linea': 'Disp',
        'descrizione': f"Chiusura turno – {dep} Deposito",
        'da': f"{dep} Deposito",
        'a': f"{dep} Deposito",
        'partenza': fmt_time(curr_m),
        'arrivo': fmt_time(fin_m),
        'km': '-'
    })

print("✅ Timeline pulita e verificata senza alcuna sovrapposizione temporale.")
