#!/usr/bin/env python3
import json
import copy

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

turni_ottimizzati = []

for t_orig in turni_reali:
    t = copy.deepcopy(t_orig)
    code = t['codice_turno']
    dep = t.get('deposito', 'Deposito')
    
    if code in ['Pi0070', 'Bo3020']:
        turni_ottimizzati.append(t)
        continue
        
    in_m = parse_m(t.get('inizio_servizio'))
    nastro_orig_m = t.get('nastro_m', parse_m(t.get('nastro')))
    rip_orig = float(str(t.get('num_riprese', '1')).replace(',', '.'))
    
    if nastro_orig_m > 510 or rip_orig >= 2.0:
        nastro_target_m = 390
        rip_opt = 1
        desc = "Compattato in Turno Continuo (1 Ripresa)"
        nome = f"{t['nome_turno']} [OTTIMIZZATO CONTINUO]"
    else:
        nastro_target_m = nastro_orig_m
        rip_opt = int(rip_orig)
        desc = "Turno Regolare Conforme"
        nome = t['nome_turno']
        
    att_raw = [a for a in t.get('attivita', []) if a.get('linea') != 'Sosta']
    
    att_clean = []
    for a in att_raw:
        p_m = parse_m(a.get('partenza'))
        arr_m = parse_m(a.get('arrivo'))
        delta_p = p_m - in_m if p_m >= in_m else (1440 - in_m + p_m)
        
        if delta_p < nastro_target_m - 15:
            sovrappone = False
            for prev in att_clean:
                p_prev = parse_m(prev.get('partenza'))
                arr_prev = parse_m(prev.get('arrivo'))
                if p_prev <= p_m < arr_prev:
                    sovrappone = True
                    break
            if not sovrappone:
                att_clean.append(a)
                
    att_clean = sorted(att_clean, key=lambda x: parse_m(x.get('partenza')))
    
    timeline = []
    curr_time_m = in_m
    sosta_inserita = False
    
    if att_clean:
        p1_m = parse_m(att_clean[0].get('partenza'))
        if p1_m > curr_time_m:
            timeline.append({
                'linea': 'Disp',
                'descrizione': f"Presa servizio e controllo livelli autobus – {dep} Deposito",
                'da': f"{dep} Deposito",
                'a': f"{dep} Deposito",
                'partenza': fmt_time(curr_time_m),
                'arrivo': fmt_time(p1_m),
                'km': '-'
            })
            curr_time_m = p1_m
            
    for i in range(len(att_clean)):
        p_i = parse_m(att_clean[i].get('partenza'))
        arr_i = parse_m(att_clean[i].get('arrivo'))
        
        if p_i > curr_time_m:
            gap = p_i - curr_time_m
            loc = timeline[-1].get('a') if timeline else f"{dep} Deposito"
            timeline.append({
                'linea': 'Sosta',
                'descrizione': f"☕ Sosta / Stacco al Deposito ({fmt_durata(gap)}) – {loc}",
                'da': loc,
                'a': loc,
                'partenza': fmt_time(curr_time_m),
                'arrivo': fmt_time(p_i),
                'km': '-',
                'durata_sosta_m': gap,
                'is_sosta_deposito': True
            })
            if gap >= 30:
                sosta_inserita = True
            
        # Inserimento sosta prima della 6a ora (se siamo attorno alla 3a/4a ora)
        if not sosta_inserita and (curr_time_m - in_m) >= 150 and nastro_target_m > 360:
            loc_s = timeline[-1].get('a') if timeline else f"{dep} Deposito"
            timeline.append({
                'linea': 'Sosta',
                'descrizione': f"☕ Sosta Obbligatoria CCNL (30 min) – {loc_s}",
                'da': loc_s,
                'a': loc_s,
                'partenza': fmt_time(curr_time_m),
                'arrivo': fmt_time(curr_time_m + 30),
                'km': '-',
                'durata_sosta_m': 30,
                'is_sosta_deposito': True
            })
            curr_time_m += 30
            sosta_inserita = True
            
        timeline.append(att_clean[i])
        curr_time_m = arr_i

    # Se ancora manca la sosta ed il nastro supera 6h
    if not sosta_inserita and nastro_target_m > 360:
        loc_s = timeline[-1].get('a') if timeline else f"{dep} Deposito"
        timeline.append({
            'linea': 'Sosta',
            'descrizione': f"☕ Sosta Obbligatoria CCNL (30 min) – {loc_s}",
            'da': loc_s,
            'a': loc_s,
            'partenza': fmt_time(curr_time_m),
            'arrivo': fmt_time(curr_time_m + 30),
            'km': '-',
            'durata_sosta_m': 30,
            'is_sosta_deposito': True
        })
        curr_time_m += 30

    target_fin_m = in_m + nastro_target_m
    if curr_time_m < target_fin_m - 10:
        timeline.append({
            'linea': 'Disp',
            'descrizione': f"Presenza e disponibilità operativa in rimessa – {dep} Deposito",
            'da': f"{dep} Deposito",
            'a': f"{dep} Deposito",
            'partenza': fmt_time(curr_time_m),
            'arrivo': fmt_time(target_fin_m - 10),
            'km': '-'
        })
        curr_time_m = target_fin_m - 10

    fin_m = curr_time_m + 10
    timeline.append({
        'linea': 'Disp',
        'descrizione': f"Rientro deposito e chiusura turno continuo – {dep} Deposito",
        'da': f"{dep} Deposito",
        'a': f"{dep} Deposito",
        'partenza': fmt_time(curr_time_m),
        'arrivo': fmt_time(fin_m),
        'km': '-'
    })

    nastro_m = (fin_m - in_m) if fin_m >= in_m else (1440 - in_m + fin_m)

    t['nome_turno'] = nome
    t['inizio_servizio'] = fmt_time(in_m)
    t['fine_servizio'] = fmt_time(fin_m)
    t['nastro'] = f"{nastro_m/60:.2f}"
    t['nastro_str'] = fmt_durata(nastro_m)
    t['nastro_m'] = nastro_m
    t['ore_lavoro'] = f"{nastro_m/60:.2f}"
    t['olg_str'] = fmt_durata(nastro_m)
    t['olg_m'] = nastro_m
    t['num_riprese'] = '1,00' if rip_opt == 1 else '2,00'
    t['num_riprese_val'] = rip_opt
    t['tipo_ottimizzazione'] = desc
    t['attivita'] = timeline

    turni_ottimizzati.append(t)

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni_ottimizzati, f, ensure_ascii=False, indent=2)

print("✅ Generazione perfetta completata!")
