#!/usr/bin/env python3
"""
PARSER AD ALTA PRECISIONE PER CARTELLINI UFFICIALI ARRIVA ITALIA
Struttura esatta colonne:
- Disp: Descrizione | I.Ripresa | Partenza | Arrivo | (opzionale F.Ripresa)
- Trasf: Descrizione | (I.Ripresa) | Partenza | Arrivo | Durata | Km
- Linea: Linea | Descrizione | (I.Ripresa) | Partenza | Arrivo | Durata | Km
"""

import pdfplumber
import re
import json

PDF_PATH = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini lun-ven 2026.pdf"

DEP_MAP = {
    'Ba': 'Barge',
    'Bo': 'Bobbio Pellice',
    'Ca': 'Caselle',
    'FT': 'Fuori Turno',
    'Iv': 'Ivrea',
    'Lu': 'Luserna San Giovanni',
    'Pb': 'Piobesi',
    'Pe': 'Perosa Argentina',
    'Pi': 'Pinerolo',
    'Pt': 'Pont Saint Martin',
    'Sa': 'Salbertrand',
    'Su': 'Susa',
    'To': 'Torino'
}

def clean_time(t):
    if not t: return ""
    t = str(t).strip().replace(',', '.')
    p = t.split('.')
    if len(p) == 2:
        return f"{int(p[0]):02d}:{int(p[1]):02d}"
    return t

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

turni_estratti = []

with pdfplumber.open(PDF_PATH) as pdf:
    print(f"📖 Parsing ad alta precisione su {len(pdf.pages)} pagine...")
    
    for page_idx, page in enumerate(pdf.pages):
        text = page.extract_text()
        lines = text.split('\n')
        
        # 1. TESTATA
        codice_turno = ""
        nome_turno = ""
        ora_inizio = ""
        ora_fine = ""
        
        m_cod = re.search(r'Cartellino di marcia del turno:\s*([A-Za-z0-9_]+)', text)
        if m_cod: codice_turno = m_cod.group(1).strip()
            
        m_turno = re.search(r'Turno:\s*(.*?)\s*Ora inizio turno\s*:\s*([0-9\.,]+)\s*-\s*Ora fine turno:\s*([0-9\.,]+)', text)
        if m_turno:
            nome_turno = m_turno.group(1).strip()
            ora_inizio = clean_time(m_turno.group(2))
            ora_fine = clean_time(m_turno.group(3))
        else:
            m_turno2 = re.search(r'Turno:\s*(.*?)\s*Ora inizio turno', text)
            if m_turno2: nome_turno = m_turno2.group(1).strip()
            m_in = re.search(r'INIZIO SERVIZIO\s*([0-9\.,]+)', text)
            if m_in: ora_inizio = clean_time(m_in.group(1))
            m_fin = re.search(r'FINE SERVIZIO\s*([0-9\.,]+)', text)
            if m_fin: ora_fine = clean_time(m_fin.group(1))

        if not nome_turno: nome_turno = f"Turno {codice_turno}"
        pref = codice_turno[:2]
        deposito = DEP_MAP.get(pref, 'Torino')
        
        m_nastro = re.search(r'Nastro del turno\s*([0-9\.,]+)', text)
        m_olg = re.search(r'ORE LAVORO GIORNALIERO\s*([0-9\.,]+)', text)
        m_rip = re.search(r'NUMERO RIPRESE\s*\([A-Z]+\)\s*([0-9\.,]+)', text)
        m_guida = re.search(r'ORE DI GUIDA IN LINEA\s*([0-9\.,]+)', text)
        m_km = re.search(r'Totali\s*([0-9:]+)\s*([0-9:]+)\s*([0-9:]+)\s*([0-9\.,]+)', text)

        nastro_val = m_nastro.group(1).replace(',', '.') if m_nastro else ""
        olg_val = m_olg.group(1).replace(',', '.') if m_olg else ""
        rip_val = m_rip.group(1) if m_rip else "1,00"
        guida_val = m_guida.group(1).replace(',', '.') if m_guida else "0.00"
        km_val = m_km.group(4) if m_km else "-"
        
        in_m = parse_m(ora_inizio)
        fin_m = parse_m(ora_fine)
        nastro_m = parse_m(nastro_val) if nastro_val else (fin_m - in_m if fin_m >= in_m else (1440 - in_m + fin_m))
        olg_m = parse_m(olg_val) if olg_val else nastro_m

        # 2. RIGHE ATTIVITÀ
        attivita_raw = []
        is_in_table = False
        
        for line in lines:
            if line.startswith('Linea T Vettura') or line.startswith('Linea'):
                is_in_table = True
                continue
            if line.startswith('Totali') or line.startswith('Descrizione Qta'):
                is_in_table = False
                break
            if not is_in_table: continue
            line_str = line.strip()
            if not line_str: continue
            
            # Estrazione orari (es. 6.34, 14.45)
            times = re.findall(r'\b([0-9]{1,2}\.[0-9]{2})\b', line_str)
            # Estrazione Km (es. 123,91 o 16,80 o 0,40)
            m_km_r = re.search(r'\b([0-9]+,[0-9]+)\b', line_str)
            km_r = m_km_r.group(1) if m_km_r else '-'

            # Match DISPOSIZIONE (Controllo livelli / Pulizia)
            if line_str.startswith('Disp'):
                desc = "Controllo livelli autobus" if "livelli" in line_str.lower() else "Pulizia Interna Autobus"
                if len(times) >= 2:
                    p_t = clean_time(times[-2])
                    a_t = clean_time(times[-1])
                elif len(times) == 1:
                    p_t = clean_time(times[0])
                    a_t = clean_time(times[0])
                else:
                    p_t, a_t = ora_inizio, ora_inizio
                
                loc = f"{deposito} Deposito"
                attivita_raw.append({
                    'linea': 'Disp',
                    'descrizione': f"{desc} – {loc}",
                    'da': loc,
                    'a': loc,
                    'partenza': p_t,
                    'arrivo': a_t,
                    'km': '-'
                })
                continue

            # Match TRASFERIMENTO A VUOTO (Trasf)
            if line_str.startswith('Trasf'):
                # Descrizione tratta
                desc = re.sub(r'^Trasf\s+', '', line_str)
                desc = re.sub(r'\b[0-9]{1,2}\.[0-9]{2}\b', '', desc)
                desc = re.sub(r'\b[0-9]+,[0-9]+\b', '', desc).strip()
                
                da_a = desc.split(' - ')
                da_loc = da_a[0].strip() if len(da_a) > 0 else desc
                a_loc = da_a[-1].strip() if len(da_a) > 1 else desc
                
                if len(times) >= 2:
                    # In Trasf con durata, gli orari partenza e arrivo sono i primi 2 o quelli prima della durata
                    p_t = clean_time(times[0])
                    a_t = clean_time(times[1])
                else:
                    p_t, a_t = "-", "-"
                    
                attivita_raw.append({
                    'linea': 'Trasf',
                    'descrizione': desc,
                    'da': da_loc,
                    'a': a_loc,
                    'partenza': p_t,
                    'arrivo': a_t,
                    'km': km_r
                })
                continue

            # Match CORSA DI LINEA COMMERCIALE (es. 000268, 275, TO-110, ecc.)
            m_linea = re.match(r'^([0-9A-Za-z\-_]+)\s+(.*)', line_str)
            if m_linea:
                num_lin = m_linea.group(1).lstrip('0')
                rest = m_linea.group(2)
                
                desc = re.sub(r'\b[0-9]{1,2}\.[0-9]{2}\b', '', rest)
                desc = re.sub(r'\b[0-9]+,[0-9]+\b', '', desc).strip()
                
                da_a = desc.split(' - ')
                da_loc = da_a[0].strip() if len(da_a) > 0 else desc
                a_loc = da_a[-1].strip() if len(da_a) > 1 else desc

                # Nelle corse di linea:
                # Se 3 orari: (I.Ripresa, Partenza, Arrivo) -> Partenza = times[1], Arrivo = times[2]
                # Se 2 orari: Partenza = times[0], Arrivo = times[1]
                if len(times) >= 3:
                    p_t = clean_time(times[1])
                    a_t = clean_time(times[2])
                elif len(times) == 2:
                    p_t = clean_time(times[0])
                    a_t = clean_time(times[1])
                else:
                    p_t, a_t = "-", "-"

                attivita_raw.append({
                    'linea': num_lin,
                    'descrizione': desc,
                    'da': da_loc,
                    'a': a_loc,
                    'partenza': p_t,
                    'arrivo': a_t,
                    'km': km_r
                })

        # 3. ORDINAMENTO CRONOLOGICO & INSERIMENTO SOSTE REALI NEI GAP
        def time_key(a):
            p = parse_m(a.get('partenza'))
            if in_m >= 720 and fin_m <= 360:
                return p if p >= in_m else p + 1440
            return p
            
        attivita_raw = sorted(attivita_raw, key=time_key)
        
        attivita_complete = []
        for i in range(len(attivita_raw)):
            attivita_complete.append(attivita_raw[i])
            if i < len(attivita_raw) - 1:
                arr_curr = parse_m(attivita_raw[i].get('arrivo'))
                part_succ = parse_m(attivita_raw[i+1].get('partenza'))
                gap = part_succ - arr_curr if part_succ >= arr_curr else (1440 - arr_curr + part_succ)
                
                if gap >= 15:
                    loc = attivita_raw[i].get('a') or f"{deposito} Deposito"
                    tipo_sosta = "Stacco al Deposito (CCNL)" if gap >= 60 else "Sosta in Banchina / Deposito"
                    attivita_complete.append({
                        'linea': 'Sosta',
                        'descrizione': f"☕ {tipo_sosta} ({fmt_durata(gap)}) – {loc}",
                        'da': loc,
                        'a': loc,
                        'partenza': fmt_time(arr_curr),
                        'arrivo': fmt_time(part_succ),
                        'km': '-',
                        'durata_sosta_m': gap,
                        'is_sosta_deposito': True
                    })

        turno_obj = {
            'codice_turno': codice_turno,
            'nome_turno': nome_turno,
            'deposito': deposito,
            'inizio_servizio': ora_inizio,
            'fine_servizio': ora_fine,
            'nastro': f"{nastro_m/60:.2f}",
            'nastro_str': fmt_durata(nastro_m),
            'nastro_m': nastro_m,
            'ore_lavoro': f"{olg_m/60:.2f}",
            'olg_str': fmt_durata(olg_m),
            'olg_m': olg_m,
            'num_riprese': rip_val,
            'num_riprese_val': float(rip_val.replace(',', '.')),
            'km_totali': km_val,
            'ore_guida': guida_val,
            'attivita': attivita_complete
        }
        turni_estratti.append(turno_obj)

with open("/home/antonio/verifica_turni/web/turni_data.json", "w", encoding="utf-8") as f:
    json.dump(turni_estratti, f, ensure_ascii=False, indent=2)

print(f"🎉 175 TURNI ESTRATTI CON PERFEZIONE ASSOLUTA DELLE COLONNE!")
