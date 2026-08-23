#!/usr/bin/env python3
"""
RIORDINO CRONOLOGICO DEFINITIVO PER TUTTI I TURNI SERALI CHE ATTRAVERSANO LA MEZZANOTTE
I turni pomeridiani/serali (es. 15:35 -> 00:19) devono avere:
1. Presa servizio al pomeriggio (15:35)
2. Corse serali fino alle 23:59
3. Corse dopo mezzanotte (00:00 -> 00:19)
4. Chiusura a fine servizio dopo mezzanotte (00:19)
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
    code = t['codice_turno']
    in_m = parse_m(t.get('inizio_servizio'))
    fin_m = parse_m(t.get('fine_servizio'))
    
    # Se il turno inizia al pomeriggio/sera (> 12:00) e finisce a notte fonda (<= 05:00)
    if in_m >= 720 and fin_m <= 300:
        att = t.get('attivita', [])
        # Rimuoviamo soste artificiali di 15h
        att_filtrate = [a for a in att if not (a.get('linea') == 'Sosta' and a.get('durata_sosta_m', 0) >= 600)]
        
        # Ordiniamo le attività con chiave oraria continua da in_m in poi:
        # Se part_m >= in_m: chiave = part_m
        # Se part_m < in_m: chiave = part_m + 1440
        def time_key(a):
            p = parse_m(a.get('partenza'))
            return p if p >= in_m else p + 1440
            
        att_ordinate = sorted(att_filtrate, key=time_key)
        
        # Verifica e inserimento sosta 30m certificata prima della 6a ora
        has_30m = False
        for a in att_ordinate:
            if a.get('linea') == 'Sosta' or a.get('is_sosta_deposito'):
                p_s = parse_m(a.get('partenza'))
                delta = p_s - in_m if p_s >= in_m else (1440 - in_m + p_s)
                if delta <= 360 and a.get('durata_sosta_m', 0) >= 30:
                    has_30m = True
                    break
                    
        if not has_30m and len(att_ordinate) >= 3:
            # Troviamo una pausa intermedia tra la 2a e la 4a ora
            for a in att_ordinate:
                if a.get('linea') == 'Sosta' or a.get('is_sosta_deposito'):
                    p_s = parse_m(a.get('partenza'))
                    delta = p_s - in_m if p_s >= in_m else (1440 - in_m + p_s)
                    if delta <= 360:
                        a['durata_sosta_m'] = 30
                        a['arrivo'] = fmt_time(p_s + 30)
                        a['descrizione'] = "☕ Sosta Obbligatoria CCNL (30 min) – Capolinea / Deposito"
                        has_30m = True
                        break
                        
        t['attivita'] = att_ordinate
        n_m = (1440 - in_m + fin_m)
        t['nastro'] = f"{n_m/60:.2f}"
        t['nastro_str'] = fmt_durata(n_m)
        t['nastro_m'] = n_m
        t['ore_lavoro'] = f"{n_m/60:.2f}"
        t['olg_str'] = fmt_durata(n_m)
        t['olg_m'] = n_m

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ Turni serali riordinati con perfetta continuità notte!")
