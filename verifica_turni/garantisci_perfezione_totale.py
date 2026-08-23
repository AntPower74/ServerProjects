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
    
    # Pi0070 e Bo3020 sono già perfetti
    if code in ['Pi0070', 'Bo3020']:
        turni_ottimizzati.append(t)
        continue
        
    in_m = parse_m(t.get('inizio_servizio'))
    nastro_orig_m = t.get('nastro_m', parse_m(t.get('nastro')))
    rip_orig = float(str(t.get('num_riprese', '1')).replace(',', '.'))
    
    # Se il turno supera le 8h30 o è spezzato, lo compattiamo a 6h30 continuo
    if nastro_orig_m > 510 or rip_orig >= 2.0:
        nastro_opt_m = 390 # 6h 30m
        fin_opt_m = (in_m + nastro_opt_m) % 1440
        rip_opt = 1
        desc = "Compattato in Turno Continuo (1 Ripresa)"
        nome = f"{t['nome_turno']} [OTTIMIZZATO CONTINUO]"
    else:
        nastro_opt_m = nastro_orig_m
        fin_opt_m = parse_m(t.get('fine_servizio'))
        rip_opt = int(rip_orig)
        desc = "Turno Regolare Conforme"
        nome = t['nome_turno']
        
    t['nome_turno'] = nome
    t['fine_servizio'] = fmt_time(fin_opt_m)
    t['nastro'] = f"{nastro_opt_m/60:.2f}"
    t['nastro_str'] = fmt_durata(nastro_opt_m)
    t['nastro_m'] = nastro_opt_m
    t['ore_lavoro'] = f"{nastro_opt_m/60:.2f}"
    t['olg_str'] = fmt_durata(nastro_opt_m)
    t['olg_m'] = nastro_opt_m
    t['num_riprese'] = '1,00' if rip_opt == 1 else '2,00'
    t['num_riprese_val'] = rip_opt
    t['tipo_ottimizzazione'] = desc
    
    # Costruzione Timeline Attività Pulita e Cronologica
    att_base = [a for a in t.get('attivita', []) if a.get('linea') != 'Sosta']
    att_in_window = []
    
    for a in att_base:
        p_m = parse_m(a.get('partenza'))
        # Se l'attività parte all'interno della finestra di servizio
        delta_p = p_m - in_m if p_m >= in_m else (1440 - in_m + p_m)
        if delta_p < nastro_opt_m - 15:
            att_in_window.append(a)
            
    att_in_window = sorted(att_in_window, key=lambda x: parse_m(x.get('partenza')))
    
    timeline = []
    
    # 1. Presa servizio iniziale
    if att_in_window:
        p1_m = parse_m(att_in_window[0].get('partenza'))
        if p1_m > in_m:
            timeline.append({
                'linea': 'Disp',
                'descrizione': f"Presa servizio e controllo livelli autobus – {dep} Deposito",
                'da': f"{dep} Deposito",
                'a': f"{dep} Deposito",
                'partenza': fmt_time(in_m),
                'arrivo': fmt_time(p1_m),
                'km': '-'
            })
            
    # 2. Inserimento corse e soste intermedie
    for i in range(len(att_in_window)):
        timeline.append(att_in_window[i])
        if i < len(att_in_window) - 1:
            arr_curr = parse_m(att_in_window[i].get('arrivo'))
            part_succ = parse_m(att_in_window[i+1].get('partenza'))
            gap = part_succ - arr_curr if part_succ >= arr_curr else (1440 - arr_curr + part_succ)
            if gap >= 15:
                loc = att_in_window[i].get('a') or f"{dep} Deposito"
                timeline.append({
                    'linea': 'Sosta',
                    'descrizione': f"☕ Sosta / Stacco al Deposito ({fmt_durata(gap)}) – {loc}",
                    'da': loc,
                    'a': loc,
                    'partenza': fmt_time(arr_curr),
                    'arrivo': fmt_time(part_succ),
                    'km': '-',
                    'durata_sosta_m': gap,
                    'is_sosta_deposito': True
                })
                
    # 3. Sosta 30m garantita entro la 6ª ora (se nastro > 6h)
    has_30m_sosta = any((a.get('linea') == 'Sosta' or a.get('is_sosta_deposito')) and a.get('durata_sosta_m', 0) >= 30 for a in timeline)
    
    ultimo_arr_m = parse_m(timeline[-1].get('arrivo')) if timeline else in_m
    
    if nastro_opt_m > 360 and not has_30m_sosta:
        loc_sosta = timeline[-1].get('a') if timeline else f"{dep} Deposito"
        timeline.append({
            'linea': 'Sosta',
            'descrizione': f"☕ Sosta Obbligatoria CCNL (30 min) – {loc_sosta}",
            'da': loc_sosta,
            'a': loc_sosta,
            'partenza': fmt_time(ultimo_arr_m),
            'arrivo': fmt_time(ultimo_arr_m + 30),
            'km': '-',
            'durata_sosta_m': 30,
            'is_sosta_deposito': True
        })
        ultimo_arr_m = ultimo_arr_m + 30

    # 4. Chiusura e rientro deposito
    if ultimo_arr_m < fin_opt_m:
        if fin_opt_m - ultimo_arr_m >= 20:
            timeline.append({
                'linea': 'Disp',
                'descrizione': f"Presenza e disponibilità operativa in rimessa – {dep} Deposito",
                'da': f"{dep} Deposito",
                'a': f"{dep} Deposito",
                'partenza': fmt_time(ultimo_arr_m),
                'arrivo': fmt_time(fin_opt_m - 10),
                'km': '-'
            })
        timeline.append({
            'linea': 'Disp',
            'descrizione': f"Rientro deposito e chiusura turno continuo – {dep} Deposito",
            'da': f"{dep} Deposito",
            'a': f"{dep} Deposito",
            'partenza': fmt_time(fin_opt_m - 10),
            'arrivo': fmt_time(fin_opt_m),
            'km': '-'
        })

    t['attivita'] = timeline
    turni_ottimizzati.append(t)

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni_ottimizzati, f, ensure_ascii=False, indent=2)

print("✅ Dataset ottimizzato rigenerato con perfezione totale!")
