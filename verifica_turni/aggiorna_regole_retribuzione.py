import json
import re

def parse_clock(t_str):
    if not t_str: return 0
    clean = str(t_str).strip().replace('.', ':').replace(',', ':')
    p = clean.split(':')
    if len(p) == 2:
        try: return int(p[0]) * 60 + int(p[1])
        except: return 0
    return 0

def fmt_time(m):
    h = (int(m) // 60) % 24
    mins = int(round(m)) % 60
    return f"{h:02d}:{mins:02d}"

def fmt_durata(m):
    if not m or m < 0: return "0h 00m"
    h = int(m) // 60
    mins = int(round(m)) % 60
    return f"{h}h {mins:02d}m"

def calcola_retribuzione_turno(t):
    dep_turno = (t.get('deposito') or '').lower()
    code_turno = (t.get('codice_turno') or '')
    dep_prefix = code_turno[:2].lower()
    
    # Mappa prefisso codice -> parole chiave deposito di residenza
    dep_map = {
        'to': ['torino', 'c.so bolzano', 'bolzano'],
        'pi': ['pinerolo'],
        'pe': ['perosa'],
        'pt': ['pont st. martin', 'pont saint martin', 'pont'],
        'su': ['susa'],
        'pb': ['piobesi'],
        'ca': ['caselle'],
        'sa': ['salbertrand'],
        'lu': ['luserna'],
        'ba': ['barge'],
        'iv': ['ivrea'],
        'bo': ['bobbio pellice', 'bobbio']
    }
    
    keywords_residenza = dep_map.get(dep_prefix, [dep_turno]) if dep_prefix in dep_map else [dep_turno]
    if dep_turno and dep_turno not in keywords_residenza:
        keywords_residenza.append(dep_turno)
        
    tot_minuti_retribuiti = 0
    
    for a in t.get('attivita', []):
        p = parse_clock(a.get('partenza'))
        arr = parse_clock(a.get('arrivo'))
        dur = arr - p if arr >= p else (1440 - p + arr)
        
        linea = a.get('linea')
        is_sosta = (linea == 'Sosta') or a.get('is_sosta_deposito')
        
        if not is_sosta:
            tot_minuti_retribuiti += dur
            a['retribuzione_pct'] = "100%"
            a['minuti_retribuiti'] = dur
        else:
            desc = ((a.get('descrizione') or '') + ' ' + (a.get('da') or '') + ' ' + (a.get('a') or '')).lower()
            
            is_in_residenza = any(k in desc for k in keywords_residenza if k)
            
            if dur <= 30:
                retrib_sosta = dur
                a['retribuzione_dettaglio'] = f"100% (≤ 30 min) = {dur}m"
            else:
                base_30 = 30
                eccedenza = dur - 30
                if is_in_residenza:
                    quota_ecc = 0
                    a['retribuzione_dettaglio'] = f"30m al 100% + {eccedenza}m al 0% (in residenza) = 30m"
                else:
                    quota_ecc = eccedenza * 0.12
                    a['retribuzione_dettaglio'] = f"30m al 100% + {eccedenza}m al 12% (fuori residenza) = {30+quota_ecc:.1f}m"
                retrib_sosta = base_30 + quota_ecc
                
            tot_minuti_retribuiti += retrib_sosta
            a['minuti_retribuiti'] = round(retrib_sosta, 1)
            a['is_residenza'] = is_in_residenza
            
    return round(tot_minuti_retribuiti)

# Aggiornamento turni_ottimizzati_completi.json
with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni_opt = json.load(f)

for t in turni_opt:
    olg_retrib = calcola_retribuzione_turno(t)
    t['olg_m'] = olg_retrib
    t['olg_str'] = fmt_durata(olg_retrib)
    t['ore_lavoro'] = f"{olg_retrib/60:.2f}"

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni_opt, f, ensure_ascii=False, indent=2)

print("✅ turni_ottimizzati_completi.json aggiornato con la formula retributiva CCNL esatta.")
