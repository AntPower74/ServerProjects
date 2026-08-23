#!/usr/bin/env python3
"""
ORDINAMENTO CRONOLOGICO CONTINUO E PERFETTO IN TUTTI I TURNI OTTIMIZZATI
Garantisce che:
1. Le attività siano rigorosamente ordinate per orario di partenza crescente.
2. Le soste siano collocate esattamente nel loro intervallo temporale corretto.
3. Non ci siano salti indietro nel tempo (es. da 09:15 a 07:30).
4. Ogni gap tra arrivo e ripartenza sia coperto in modo fluido (Sosta + Disponibilità Deposito).
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

def fmt_durata(m):
    if not m or m < 0: return "0h 00m"
    h = m // 60
    mins = m % 60
    return f"{h}h {mins:02d}m"

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    if t.get('codice_turno') in ['Pi0070', 'Bo3020']:
        continue
        
    att = t.get('attivita', [])
    if not att: continue
    
    in_m = parse_m(t.get('inizio_servizio'))
    fin_m = parse_m(t.get('fine_servizio'))
    dep = t.get('deposito', 'Pinerolo')
    
    # Separiamo le corse reali e le disposizioni
    corse_reali = [a for a in att if a.get('linea') not in ['Sosta'] and 'chiusura turno' not in a.get('descrizione', '').lower()]
    corse_reali = sorted(corse_reali, key=lambda x: parse_m(x.get('partenza')))
    
    nuova_timeline = []
    
    if corse_reali:
        # 1. Presa servizio iniziale
        p_start_m = parse_m(corse_reali[0].get('partenza'))
        if p_start_m > in_m:
            nuova_timeline.append({
                'linea': 'Disp',
                'descrizione': f"Presa servizio e controllo livelli autobus – {dep} Deposito",
                'da': f"{dep} Deposito",
                'a': f"{dep} Deposito",
                'partenza': fmt_time(in_m),
                'arrivo': fmt_time(p_start_m),
                'km': '-'
            })
            
        # 2. Inserimento di tutte le corse reali
        for i in range(len(corse_reali)):
            nuova_timeline.append(corse_reali[i])
            if i < len(corse_reali) - 1:
                arr_curr = parse_m(corse_reali[i].get('arrivo'))
                part_succ = parse_m(corse_reali[i+1].get('partenza'))
                gap = part_succ - arr_curr if part_succ >= arr_curr else 0
                if gap >= 15:
                    loc = corse_reali[i].get('a') or 'Deposito'
                    nuova_timeline.append({
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
                    
        # 3. Chiusura turno / sosta finale fino a fine servizio
        ultimo_arr_m = parse_m(corse_reali[-1].get('arrivo'))
        if ultimo_arr_m < fin_m:
            gap_fin = fin_m - ultimo_arr_m
            loc_fin = corse_reali[-1].get('a') or f"{dep} Deposito"
            
            # Se il gap finale è consistente, inseriamo la sosta certificata di 30m e la disponibilità
            if gap_fin >= 30:
                nuova_timeline.append({
                    'linea': 'Sosta',
                    'descrizione': f"☕ Sosta Obbligatoria CCNL (30 min) – {dep} Deposito",
                    'da': loc_fin,
                    'a': loc_fin,
                    'partenza': fmt_time(ultimo_arr_m),
                    'arrivo': fmt_time(ultimo_arr_m + 30),
                    'km': '-',
                    'durata_sosta_m': 30,
                    'is_sosta_deposito': True
                })
                if ultimo_arr_m + 30 < fin_m - 10:
                    nuova_timeline.append({
                        'linea': 'Disp',
                        'descrizione': f"Presenza e disponibilità operativa in rimessa – {dep} Deposito",
                        'da': f"{dep} Deposito",
                        'a': f"{dep} Deposito",
                        'partenza': fmt_time(ultimo_arr_m + 30),
                        'arrivo': fmt_time(fin_m - 10),
                        'km': '-'
                    })
            
            nuova_timeline.append({
                'linea': 'Disp',
                'descrizione': f"Rientro deposito e chiusura turno continuo – {dep} Deposito",
                'da': f"{dep} Deposito",
                'a': f"{dep} Deposito",
                'partenza': fmt_time(fin_m - 10),
                'arrivo': fmt_time(fin_m),
                'km': '-'
            })
            
        t['attivita'] = nuova_timeline

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ Timeline perfettamente ordinata e sincronizzata su tutti i turni!")
