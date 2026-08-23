import json

# 1. Funzione Python
def fmt_durata(m):
    if not m or m < 0: return "0h 00m"
    h = int(m) // 60
    mins = int(round(m)) % 60
    return f"{h}h {mins:02d}m"

def parse_clock(t_str):
    if not t_str: return 0
    clean = str(t_str).strip().replace('.', ':').replace(',', ':')
    p = clean.split(':')
    if len(p) == 2:
        try: return int(p[0]) * 60 + int(p[1])
        except: return 0
    return 0

def calcola_retribuzione_secca(t):
    dep_turno = (t.get('deposito') or '').lower()
    code_turno = (t.get('codice_turno') or '')
    dep_prefix = code_turno[:2].lower()
    
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
        
    tot_minuti = 0
    for a in t.get('attivita', []):
        p = parse_clock(a.get('partenza'))
        arr = parse_clock(a.get('arrivo'))
        dur = arr - p if arr >= p else (1440 - p + arr)
        
        linea = a.get('linea')
        is_sosta = (linea == 'Sosta') or a.get('is_sosta_deposito')
        
        if not is_sosta:
            tot_minuti += dur
        else:
            desc = ((a.get('descrizione') or '') + ' ' + (a.get('da') or '') + ' ' + (a.get('a') or '')).lower()
            is_in_residenza = any(k in desc for k in keywords_residenza if k)
            
            if dur <= 30:
                tot_minuti += dur
            else:
                if is_in_residenza:
                    tot_minuti += 0
                else:
                    tot_minuti += dur * 0.12
                    
    return round(tot_minuti)

# Aggiornamento turni_ottimizzati_completi.json
with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni_opt = json.load(f)

for t in turni_opt:
    olg_val = calcola_retribuzione_secca(t)
    t['olg_m'] = olg_val
    t['olg_str'] = fmt_durata(olg_val)
    t['ore_lavoro'] = f"{olg_val/60:.2f}"

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni_opt, f, ensure_ascii=False, indent=2)

# Aggiornamento index.html
with open("/home/antonio/verifica_turni/web/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Aggiorna la logica in calcolaOLGRetribuito
old_olg_js = r'''                    if (dur <= 30) {
                        totMinuti += dur;
                    } else {
                        totMinuti += 30;
                        const ecc = dur - 30;
                        if (!isInResidenza) {
                            totMinuti += ecc * 0.12;
                        }
                    }'''

new_olg_js = r'''                    if (dur <= 30) {
                        totMinuti += dur;
                    } else {
                        if (!isInResidenza) {
                            totMinuti += dur * 0.12;
                        }
                    }'''

html = html.replace(old_olg_js, new_olg_js)

# Aggiorna la descrizione nella card sosta in index.html
old_card_js = r'''                    if (durM <= 30) {
                        retribBadge = `<span class="text-emerald-400 font-bold">100% Retribuita</span>`;
                        retribDettaglio = `Sosta breve (&le; 30m) &bull; <b>${durM}m pagati</b>`;
                    } else {
                        const ecc = durM - 30;
                        if (isInResidenza) {
                            retribBadge = `<span class="text-amber-300 font-bold">In Residenza (30m 100% + ${ecc}m 0%)</span>`;
                            retribDettaglio = `30m al 100% + ${ecc}m al 0% (stacco residenza) = <b>30m pagati</b>`;
                        } else {
                            const q12 = (ecc * 0.12).toFixed(1);
                            const totPagato = (30 + ecc * 0.12).toFixed(1);
                            retribBadge = `<span class="text-indigo-300 font-bold">Fuori Residenza (30m 100% + ${ecc}m 12%)</span>`;
                            retribDettaglio = `30m al 100% + ${ecc}m al 12% (${q12}m) = <b>${totPagato}m pagati</b>`;
                        }
                    }'''

new_card_js = r'''                    if (durM <= 30) {
                        retribBadge = `<span class="text-emerald-400 font-bold">100% Retribuita</span>`;
                        retribDettaglio = `Sosta breve (&le; 30m) &bull; <b>${durM}m pagati al 100%</b>`;
                    } else {
                        if (isInResidenza) {
                            retribBadge = `<span class="text-slate-400 font-bold">In Residenza (0% Retribuita)</span>`;
                            retribDettaglio = `Sosta > 30m in deposito residenza &bull; <b>0m pagati (0%)</b>`;
                        } else {
                            const totPagato = (durM * 0.12).toFixed(1);
                            retribBadge = `<span class="text-indigo-300 font-bold">Fuori Residenza (12% Retribuita)</span>`;
                            retribDettaglio = `Sosta > 30m fuori residenza &bull; <b>${totPagato}m pagati (12% di ${durM}m)</b>`;
                        }
                    }'''

html = html.replace(old_card_js, new_card_js)

with open("/home/antonio/verifica_turni/web/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Aggiornamento completato: se sosta > 30m, paga 0% in residenza e solo il 12% se fuori residenza.")
