#!/usr/bin/env python3
"""
ESTRATTORE UFFICIALE E INTEGRALE CARTELLINI ARRIVA ITALIA 2026
Legge pagina per pagina "Cartellini lun-ven 2026.pdf" (175 pagine = 175 turni ufficiali).
Estrae:
- Intestazione (Codice turno, Nome turno, Ora inizio, Ora fine, Nastro, OLG, Riprese, Km, Deposito)
- Tutte le righe attività (Disp, Trasf, Linea con codice, tratte, orari esatti, km)
- Inserisce i gap come soste esplicite certificate
Salva in /home/antonio/verifica_turni/web/turni_data.json
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
    t = t.strip().replace(',', '.')
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
    print(f"📖 Inizio estrazione ufficiale su {len(pdf.pages)} pagine...")
    
    for page_idx, page in enumerate(pdf.pages):
        text = page.extract_text()
        lines = text.split('\n')
        
        # 1. METADATI TESTATA
        codice_turno = ""
        nome_turno = ""
        ora_inizio = ""
        ora_fine = ""
        
        m_cod = re.search(r'Cartellino di marcia del turno:\s*([A-Za-z0-9_]+)', text)
        if m_cod:
            codice_turno = m_cod.group(1).strip()
            
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

        if not nome_turno:
            nome_turno = f"Turno {codice_turno}"
            
        pref = codice_turno[:2]
        deposito = DEP_MAP.get(pref, 'Torino')
        
        # ORE LAVORO / NASTRO / RIPRESE dai box finali
        m_nastro = re.search(r'Nastro del turno\s*([0-9\.,]+)', text)
        m_olg = re.search(r'ORE LAVORO GIORNALIERO\s*([0-9\.,]+)', text)
        m_rip = re.search(r'NUMERO RIPRESE\s*\([A-Z]+\)\s*([0-9\.,]+)', text)
        m_guida = re.search(r'ORE DI GUIDA IN LINEA\s*([0-9\.,]+)', text)
        m_guida_tot = re.search(r'ORE DI GUIDA COMPLESSIVA\s*([0-9\.,]+)', text)
        m_km = re.search(r'Totali\s*([0-9:]+)\s*([0-9:]+)\s*([0-9:]+)\s*([0-9\.,]+)', text)

        nastro_val = m_nastro.group(1).replace(',', '.') if m_nastro else ""
        olg_val = m_olg.group(1).replace(',', '.') if m_olg else ""
        rip_val = m_rip.group(1) if m_rip else "1,00"
        guida_val = m_guida.group(1).replace(',', '.') if m_guida else "0.00"
        km_val = m_km.group(4) if m_km else "-"
        
        # Calcolo minuti
        in_m = parse_m(ora_inizio)
        fin_m = parse_m(ora_fine)
        
        if nastro_val:
            nastro_m = parse_m(nastro_val)
        else:
            nastro_m = fin_m - in_m if fin_m >= in_m else (1440 - in_m + fin_m)
            
        if olg_val:
            olg_m = parse_m(olg_val)
        else:
            olg_m = nastro_m

        # 2. ESTRAZIONE RIGHE ATTIVITÀ
        attivita_raw = []
        is_in_table = False
        
        for line in lines:
            if line.startswith('Linea T Vettura') or line.startswith('Linea'):
                is_in_table = True
                continue
            if line.startswith('Totali') or line.startswith('Descrizione Qta'):
                is_in_table = False
                break
            if not is_in_table:
                continue
                
            line_str = line.strip()
            if not line_str: continue
            
            # Match Disp
            if line_str.startswith('Disp'):
                m_disp = re.search(r'Disp\s+(.*?)\s+([0-9\.]+)\s+([0-9\.]+)(?:\s+([0-9\.]+))?', line_str)
                if m_disp:
                    desc = m_disp.group(1).strip()
                    p_t = clean_time(m_disp.group(2))
                    a_t = clean_time(m_disp.group(3))
                    attivita_raw.append({
                        'linea': 'Disp',
                        'descrizione': desc,
                        'da': desc,
                        'a': desc,
                        'partenza': p_t,
                        'arrivo': a_t,
                        'km': '-'
                    })
                continue

            # Match Trasf
            if line_str.startswith('Trasf'):
                # Trasf DESCRIZIONE PARTENZA ARRIVO ... KM
                parts = re.findall(r'([0-9]+\.[0-9]+)', line_str)
                # Trova la descrizione togliendo 'Trasf' e numeri orari
                desc = re.sub(r'^Trasf\s+', '', line_str)
                desc = re.sub(r'[0-9]+\.[0-9]+', '', desc)
                desc = re.sub(r'[0-9]+,[0-9]+', '', desc).strip()
                
                # Prendi i primi due orari come partenza e arrivo
                if len(parts) >= 2:
                    p_t = clean_time(parts[0])
                    a_t = clean_time(parts[1])
                    
                    # Estrai da e a
                    da_a = desc.split(' - ')
                    da_loc = da_a[0].strip() if len(da_a) > 0 else desc
                    a_loc = da_a[-1].strip() if len(da_a) > 1 else desc
                    
                    # Km
                    m_km_r = re.search(r'([0-9]+,[0-9]+)$', line_str)
                    km_r = m_km_r.group(1) if m_km_r else '-'
                    
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

            # Match Corse di Linea (es. 000268, 000280, 275, TO-110, ecc.)
            m_linea = re.match(r'^([0-9A-Za-z\-_]+)\s+(.*)', line_str)
            if m_linea:
                num_lin = m_linea.group(1).lstrip('0')
                rest = m_linea.group(2)
                
                times = re.findall(r'([0-9]+\.[0-9]+)', rest)
                desc = re.sub(r'[0-9]+\.[0-9]+', '', rest)
                desc = re.sub(r'[0-9]+,[0-9]+', '', desc).strip()
                
                if len(times) >= 2:
                    # In cartellini tipo SADEM, orari possono essere: (partenza, arrivo) o con intertempi
                    p_t = clean_time(times[0])
                    a_t = clean_time(times[1])
                    
                    da_a = desc.split(' - ')
                    da_loc = da_a[0].strip() if len(da_a) > 0 else desc
                    a_loc = da_a[-1].strip() if len(da_a) > 1 else desc
                    
                    m_km_r = re.search(r'([0-9]+,[0-9]+)$', line_str)
                    km_r = m_km_r.group(1) if m_km_r else '-'
                    
                    attivita_raw.append({
                        'linea': num_lin,
                        'descrizione': desc,
                        'da': da_loc,
                        'a': a_loc,
                        'partenza': p_t,
                        'arrivo': a_t,
                        'km': km_r
                    })

        # 3. ORDINAMENTO E INSERIMENTO SOSTE CERTIFICATE NEI GAP
        # Ordiniamo in base alla partenza dal momento in_m
        def time_key(a):
            p = parse_m(a.get('partenza'))
            if in_m >= 720 and fin_m <= 360: # Notturno/serale
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
                    loc = attivita_raw[i].get('a') or 'Deposito'
                    attivita_complete.append({
                        'linea': 'Sosta',
                        'descrizione': f"☕ Sosta / Stacco in Deposito o Banchina ({fmt_durata(gap)}) – {loc}",
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

print(f"\n✅ Estrazione completata con successo su tutti i {len(turni_estratti)} turni ufficiali!")

with open("/home/antonio/verifica_turni/web/turni_data.json", "w", encoding="utf-8") as f:
    json.dump(turni_estratti, f, ensure_ascii=False, indent=2)

print("📁 Salvato /home/antonio/verifica_turni/web/turni_data.json")
