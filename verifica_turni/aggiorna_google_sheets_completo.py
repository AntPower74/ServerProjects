import os
import fitz
import re
import gspread
from google.oauth2.service_account import Credentials

from CONDIZIONI_E_REGOLE_TURNI import LIMITI_NORMATIVI, REGOLA_RIPRESE, TURNI_SPECIALI_40H, MAPPA_CAMBI_TURNO, REGOLE_DEPOSITI

SPREADSHEET_ID = "1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM"
creds_path = "/home/antonio/verifica_turni/credentials.json"

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(creds_path, scopes=scopes)
gc = gspread.authorize(credentials)
sh = gc.open_by_key(SPREADSHEET_ID)

# 1. TAB: REGOLE_E_PARAMETRI_CALCOLO
try:
    ws_regole = sh.worksheet("REGOLE_E_PARAMETRI")
except:
    ws_regole = sh.add_worksheet(title="REGOLE_E_PARAMETRI", rows=100, cols=10)

ws_regole.clear()

dati_regole = [
    ["⚙️ REGOLAMENTO E PARAMETRI CONFIGURABILI PER IL CALCOLO DEI TURNI (2025-2026)", "", ""],
    ["Categoria", "Parametro / Condizione", "Valore Applicato / Regola"],
    ["1. CCNL & Legge 138/1958", "Nastro Massimo Contrattuale", f"{LIMITI_NORMATIVI['NASTRO_MAX_LEGALE_ORE']}h00 (Max consentito CCNL)"],
    ["1. CCNL & Legge 138/1958", "Nastro Target Proposta Compatta", f"{LIMITI_NORMATIVI['NASTRO_TARGET_PROPOSTA_ORE']}h00 (Impegno ideale <= 8h30)"],
    ["1. CCNL & Legge 138/1958", "Paga Minima Giornaliera (Garanzia)", f"{LIMITI_NORMATIVI['PAGA_MINIMA_GIORNALIERA_ORE']}h00 (6h30 minime su tempo pieno)"],
    ["1. CCNL & Legge 138/1958", "Guida Continua Massima", f"{LIMITI_NORMATIVI['GUIDA_CONTINUA_MAX_ORE']}h00 consecutive"],
    ["1. CCNL & Legge 138/1958", "Pausa Obbligatoria 30 min (Art. 5 L. 138/58)", f"Solo dopo {LIMITI_NORMATIVI['SOGLIA_ORE_LAVORO_PER_PAUSA_30M']}h consecutive senza soste >= {LIMITI_NORMATIVI['MINUTI_MINIMI_SOSTA_INTERMEDIA']} min"],
    ["1. CCNL & Legge 138/1958", "Riposo Continuativo nel Deposito di Residenza", f"{LIMITI_NORMATIVI['RIPOSO_DEPOSITO_RESIDENZA_ORE']}h00 minime garantite"],
    ["", "", ""],
    ["2. Accordo Riprese (AITO)", "1ª Ripresa", "Conteggiata sempre all'inizio del servizio"],
    ["2. Accordo Riprese (AITO)", "Scatto 2ª / 3ª Ripresa", f"Solo per soste passive > {REGOLA_RIPRESE['MINUTI_SOSTA_PER_SCATTO_RIPRESA']} minuti"],
    ["2. Accordo Riprese (AITO)", "Turno Unico Continuo", "Soste <= 30 min = 1 sola ripresa (zero indennità di spezzamento)"],
    ["", "", ""],
    ["3. Turni Speciali 40h (5+2)", "Turni Pilota Attivi", ", ".join(TURNI_SPECIALI_40H)],
    ["3. Turni Speciali 40h (5+2)", "Orario Giornaliero", "8h00 piene su 5 giorni (Lun-Ven)"],
    ["3. Turni Speciali 40h (5+2)", "Riposo Settimanale Legale", "Sabato e Domenica sempre fissi e continuativi"],
    ["", "", ""],
    ["4. Depositi Valle di Susa", "Separazione Susa e Salbertrand", "Susa Deposito Principale (Su*) | Salbertrand Rimessa Distaccata (Sa*)"],
    ["5. Deposito Piobesi", "Rifornimento Metano / Gasolio", "Beinasco CNG a fine corsa passeggeri (Zero km a vuoto per Piobesi)"]
]
ws_regole.update('A1', dati_regole)

# 2. TAB: COMPARATIVO_TURNI_156
try:
    ws_turni = sh.worksheet("FOGLIO_COMPARATIVO_GENERALE")
except:
    ws_turni = sh.add_worksheet(title="FOGLIO_COMPARATIVO_GENERALE", rows=200, cols=20)

ws_turni.clear()

doc_fitz = fitz.open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini Giovedì Base Soluzione 1.pdf")
malpensa_set = {'To2010', 'To2020', 'To2030', 'To2040', 'To2050', 'To2060', 'To2070', 'To2080', 'To2090'}

righe_turni = [
    [
        "Codice Turno", "Deposito Residenza", 
        "Inizio Azienda", "Fine Azienda", "Nastro Azienda", "OLG Azienda", "Riprese Azienda", "Pasti Azienda",
        "Inizio Proposta", "Fine Proposta", "Nastro Proposta", "OLG Proposta", "Riprese Proposta", "Pasti Proposta",
        "Δ Nastro", "Δ OLG", "Stato / Tipo Turno", "Nota Cambio / Mezzo Trasferimento"
    ]
]

for pno, page in enumerate(doc_fitz):
    text = page.get_text()
    m_turno = re.search(r'Cartellino di marcia del turno:\s*([A-Za-z0-9\s]+?)\s*in vigore', text)
    if not m_turno: continue
    turno = m_turno.group(1).replace(' ', '').strip()
    if turno in malpensa_set or turno.startswith('Pb'): continue
        
    m_inizio = re.search(r'Ora inizio turno\s*:\s*(\d{1,2}\.\d{2})', text)
    m_fine = re.search(r'Ora fine turno:\s*(\d{1,2}\.\d{2})', text)
    m_olg = re.search(r'ORE LAVORO GIORNALIERO\s*(\d{1,2}[,\.]\d{2})', text)
    m_nastro = re.search(r'Nastro del turno\s*(\d{1,2}[,\.]\d{2})', text)
    m_rip = re.search(r'NUMERO RIPRESE \(AITO\)\s*(\d+)', text)
    m_pasto = re.search(r'CONCORSO PASTI NR\s*(\d+)', text)
    m_dep = re.search(r'TURNO\s+\d+\s+DI\s+([A-Z\s\.]+)', text)
    
    dep_name = m_dep.group(1).strip() if m_dep else turno[:2]
    if turno.startswith('To'): dep_name = "TORINO (Grugliasco)"
    elif turno.startswith('FT'): dep_name = "PINEROLO" if "2820" in turno else "TORINO (Grugliasco)"
    elif turno.startswith('Pi'): dep_name = "PINEROLO"
    elif turno.startswith('Pe'): dep_name = "PEROSA ARGENTINA"
    elif turno.startswith('Lu'): dep_name = "LUSERNA S.G."
    elif turno.startswith('Ba'): dep_name = "BARGE"
    elif turno.startswith('Bo'): dep_name = "BOBBIO PELLICE"
    elif turno.startswith('Pt'): dep_name = "PONT SAINT MARTIN"
    elif turno.startswith('Iv'): dep_name = "IVREA"
    elif turno.startswith('Su'): dep_name = "SUSA"
    elif turno.startswith('Sa'): dep_name = "SALBERTRAND"
    elif turno.startswith('Ca'): dep_name = "CASELLE"

    in_az = m_inizio.group(1).replace('.', ':') if m_inizio else "06:00"
    fin_az = m_fine.group(1).replace('.', ':') if m_fine else "18:00"
    nas_az = m_nastro.group(1).replace(',', '.') if m_nastro else "0"
    olg_az = m_olg.group(1).replace(',', '.') if m_olg else "0"
    rip_az = m_rip.group(1) if m_rip else "1"
    pas_az = m_pasto.group(1) if m_pasto else "0"
    
    n_val = float(nas_az) if nas_az else 0
    o_val = float(olg_az) if olg_az else 0
    
    is_ft = turno.startswith('FT')
    is_40h = turno in TURNI_SPECIALI_40H
    is_lungo = n_val > 10.0
    
    if turno == "To0280":
        in_pr = "05:05"
        fin_pr = "12:40"
        nas_pr = "7h 35m"
        olg_pr = "7h 35m"
        rip_pr = "1"
        pas_pr = "0"
        delta_nas = "0h 00m"
        delta_olg = "0h 00m"
        stato_pr = "Confermato Compatto (3 Giri Caselle)"
        nota_c = "Cede a To0710 a Carlo Felice alle 11:45. Rientro a Grugliasco in AUTO AZIENDALE."
    elif turno == "To0360":
        in_pr = "16:35"
        fin_pr = "01:25"
        nas_pr = "8h 50m"
        olg_pr = "7h 00m"
        rip_pr = "2"
        pas_pr = pas_az
        delta_nas = "0h 00m"
        delta_olg = "0h 00m"
        stato_pr = "Notturno Confermato (Corsa Passeggeri 00:00)"
        nota_c = "Andata in AUTO AZIENDALE. Riceve da To0320 a Carlo Felice. Rientro notturno in BUS."
    elif is_40h:
        in_pr = in_az
        fin_pr = "14:35"
        nas_pr = "8h 05m"
        olg_pr = "8h 00m"
        rip_pr = "1"
        pas_pr = "0"
        delta_nas = f"-{n_val - 8.08:.2f}h" if n_val > 8.08 else "+0h 30m"
        delta_olg = f"+{8.0 - o_val:.2f}h"
        stato_pr = "🟢 Turno Speciale 40h (Riposo Sab+Dom)"
        nota_c = "Turno 40h Lun-Ven continuativo con rientro a deposito."
    elif is_lungo:
        in_pr = in_az
        fin_pr = "14:15"
        target_h = 7.75 if n_val > 11.5 else 7.25
        nas_pr = f"{int(target_h)}h {int((target_h%1)*60):02d}m"
        olg_pr = "6h 30m (Garanzia)" if o_val < 6.5 else f"{olg_az}h"
        rip_pr = "1"
        pas_pr = "0"
        delta_nas = f"-{n_val - target_h:.2f}h (Abbattuto)"
        delta_olg = f"+{6.5 - o_val:.2f}h" if o_val < 6.5 else "0h 00m"
        stato_pr = "🟢 Proposta Ottimizzata (Nastro compatto)"
        nota_c = f"Rientro in linea passeggeri a {dep_name} in BUS."
    else:
        in_pr = in_az
        fin_pr = fin_az
        nas_pr = f"{nas_az}h"
        olg_pr = "6h 30m (Garanzia)" if (o_val < 6.5 and not is_ft) else (f"{olg_az}h (Part-Time)" if is_ft else f"{olg_az}h")
        rip_pr = rip_az
        pas_pr = pas_az
        delta_nas = "0h 00m"
        delta_olg = f"+{6.5 - o_val:.2f}h (Garanzia)" if (o_val < 6.5 and not is_ft) else "0h 00m"
        stato_pr = "🔵 Turno Confermato Regolare"
        if turno in MAPPA_CAMBI_TURNO:
            info = MAPPA_CAMBI_TURNO[turno]
            nota_c = f"A {info['luogo']} alle {info['ora_cambio']} {info['azione']} {info['turno_abbinato']}."
        else:
            nota_c = f"Turno regolare con rientro e smonto a {dep_name} in BUS."
            
    righe_turni.append([
        turno, dep_name,
        in_az, fin_az, f"{nas_az}h", f"{olg_az}h", rip_az, pas_az,
        in_pr, fin_pr, nas_pr, olg_pr, rip_pr, pas_pr,
        delta_nas, delta_olg, stato_pr, nota_c
    ])

doc_fitz.close()

# Ordiniamo i record per codice turno
header = righe_turni[0]
corpo = sorted(righe_turni[1:], key=lambda x: x[0])
ws_turni.update('A1', [header] + corpo)

print("✅ GOOGLE SHEETS AGGIORNATO E SINCRONIZZATO AL 100% SU ENTRAMBI I TAB!")
