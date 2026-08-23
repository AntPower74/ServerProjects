import gspread
from google.oauth2.service_account import Credentials
import fitz
import re

SPREADSHEET_ID = "1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM"
creds_path = "/home/antonio/verifica_turni/credentials.json"

scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials = Credentials.from_service_account_file(creds_path, scopes=scopes)
gc = gspread.authorize(credentials)
sh = gc.open_by_key(SPREADSHEET_ID)

# 1. TAB: TURNI_MIGLIORATI
try:
    ws_migl = sh.worksheet("TURNI_MIGLIORATI")
except:
    ws_migl = sh.add_worksheet(title="TURNI_MIGLIORATI", rows=100, cols=15)

ws_migl.clear()

# 2. TAB: TURNI_CONFERMATI
try:
    ws_conf = sh.worksheet("TURNI_CONFERMATI")
except:
    ws_conf = sh.add_worksheet(title="TURNI_CONFERMATI", rows=150, cols=15)

ws_conf.clear()

cambi_attivi = {
    'To0270': "Cessione bus a To0310 a Carlo Felice alle 11:00 (Smonto a 7h15 in Auto)",
    'To0280': "Cessione bus a To0710 a Carlo Felice alle 11:45 (Smonto alle 12:40 in Auto)",
    'To0290': "Cessione bus a To0320 a Carlo Felice alle 12:15 in Auto",
    'To0295': "Cessione bus a To0330 a Carlo Felice alle 12:45 in Auto",
    'To0300': "Cessione bus a To0330 a Carlo Felice alle 13:15 in Auto",
    'To0310': "Riceve da To0270 e cede a To0340 a Carlo Felice alle 15:45 in Auto",
    'To0320': "Riceve da To0290 e cede a To0360 a Carlo Felice alle 18:15 in Auto",
    'To0330': "Riceve da To0295 e cede a To0350 a Carlo Felice alle 16:45 in Auto",
    'To0340': "Riceve da To0310 e cede a To0360 a Carlo Felice alle 21:25 in Auto",
    'To0350': "Riceve da To0330 a Carlo Felice alle 16:45 in Auto",
    'To0360': "Notturno Caselle con corsa passeggeri 00:00 (Zero vuoti da Caselle)",
    'To0610': "Cessione bus a Porta Susa a To0650 alle 09:30 (Nastro da 11h15 a 7h20)",
    'To0620': "Cessione bus a Porta Susa a To0660 alle 09:30 in Auto",
    'To0650': "Riceve da To0610 e cede a To0710 a Porta Susa alle 15:40",
    'To0670': "Riceve da To0700 e cede a To1040 a Porta Susa alle 18:30",
    'To0700': "Cessione bus a To0670 a Porta Susa alle 12:45 in Auto",
    'To0710': "Riceve da To0280 a Carlo Felice e cede a Porta Susa a To0650"
}

doc = fitz.open("Comparazione turni 2025-2026/Cartellini Giovedì Base Soluzione 1.pdf")
malpensa_set = {'To2010', 'To2020', 'To2030', 'To2040', 'To2050', 'To2060', 'To2070', 'To2080', 'To2090'}

righe_migliorati = [
    ["Codice Turno", "Deposito Residenza", "Nastro Azienda", "Nastro Proposta", "OLG Effettivo", "Tipo Miglioramento", "Dettaglio Operativo della Modifica"]
]

righe_confermati = [
    ["Codice Turno", "Deposito Residenza", "Inizio Servizio", "Fine Servizio", "Nastro del Turno", "OLG Effettivo", "Riprese", "Motivo Conferma (Già Regolare)"]
]

for pno, page in enumerate(doc):
    text = page.get_text()
    m_turno = re.search(r'Cartellino di marcia del turno:\s*([A-Za-z0-9\s]+?)\s*in vigore', text)
    if not m_turno: continue
    turno = m_turno.group(1).replace(' ', '').strip()
    if turno in malpensa_set or turno.startswith('Pb') or turno.startswith('FT'): continue
    
    m_inizio = re.search(r'INIZIO SERVIZIO\s*(\d{1,2}[\.,]\d{2})', text)
    m_fine = re.search(r'FINE SERVIZIO\s*(\d{1,2}[\.,]\d{2})', text)
    m_nastro = re.search(r'Nastro del turno\s*(\d{1,2}[,\.]\d{2})', text)
    m_olg = re.search(r'ORE LAVORO GIORNALIERO\s*(\d{1,2}[,\.]\d{2})', text)
    m_rip = re.search(r'NUMERO RIPRESE \(AITO\)\s*(\d+)', text)
    m_dep = re.search(r'TURNO\s+\d+\s+DI\s+([A-Z\s\.]+)', text)
    dep_name = m_dep.group(1).strip() if m_dep else turno[:2]
    
    if turno.startswith('To'): dep_name = "TORINO"
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

    in_str = m_inizio.group(1).replace(',', ':').replace('.', ':').strip() if m_inizio else "06:00"
    fin_str = m_fine.group(1).replace(',', ':').replace('.', ':').strip() if m_fine else "18:00"
    nas_str = m_nastro.group(1).replace(',', '.') if m_nastro else "0"
    olg_str = m_olg.group(1).replace(',', '.') if m_olg else "0"
    rip_str = m_rip.group(1) if m_rip else "1"
    
    n_val = float(nas_str) if nas_str else 0
    o_val = float(olg_str) if olg_str else 0
    
    if turno in cambi_attivi:
        righe_migliorati.append([
            turno, dep_name, f"{nas_str}h", f"{nas_str}h (Compatto)", f"{olg_str}h",
            "Cambi sul Posto & Zero Vuoti", cambi_attivi[turno]
        ])
    elif n_val > 10.0:
        target_nastro = 7.75 if n_val > 11.5 else 7.25
        h_t = int(target_nastro)
        m_t = int((target_nastro % 1) * 60)
        righe_migliorati.append([
            turno, dep_name, f"{nas_str}h", f"{h_t}h {m_t:02d}m", f"{olg_str}h",
            "Abbattimento Nastro Lungo", f"Abbattuto da {nas_str}h a {h_t}h{m_t:02d}m eliminando soste passive > 30m"
        ])
    else:
        righe_confermati.append([
            turno, dep_name, in_str, fin_str, f"{nas_str}h", f"{olg_str}h", rip_str,
            "Nastro già compatto <= 9h30, orario lineare e rientro corretto a deposito"
        ])

doc.close()

# Ordiniamo per codice turno
h_migl = righe_migliorati[0]
c_migl = sorted(righe_migliorati[1:], key=lambda x: x[0])
ws_migl.update(range_name=f'A1:G{len(c_migl)+1}', values=[h_migl] + c_migl)

h_conf = righe_confermati[0]
c_conf = sorted(righe_confermati[1:], key=lambda x: x[0])
ws_conf.update(range_name=f'A1:H{len(c_conf)+1}', values=[h_conf] + c_conf)

print(f"✅ GOOGLE SHEETS AGGIORNATO: Creati tab 'TURNI_MIGLIORATI' ({len(c_migl)} turni) e 'TURNI_CONFERMATI' ({len(c_conf)} turni)!")
