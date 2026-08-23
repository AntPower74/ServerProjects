import gspread
from google.oauth2.service_account import Credentials
from collections import Counter

SPREADSHEET_ID = "1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM"
creds_path = "/home/antonio/verifica_turni/credentials.json"

scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials = Credentials.from_service_account_file(creds_path, scopes=scopes)
gc = gspread.authorize(credentials)
sh = gc.open_by_key(SPREADSHEET_ID)

ws_nt = sh.worksheet("Numero turni")
rows = ws_nt.get_all_values()

# Mappa depositi pulita e affidabile da codice turno
def ricava_deposito(cod_turno):
    t = cod_turno.strip()
    if t.startswith('To'): return "TORINO"
    elif t.startswith('FT'): return "PINEROLO" if "2820" in t else "TORINO"
    elif t.startswith('Pi'): return "PINEROLO"
    elif t.startswith('Pe'): return "PEROSA ARGENTINA"
    elif t.startswith('Lu'): return "LUSERNA S.G."
    elif t.startswith('Ba'): return "BARGE"
    elif t.startswith('Bo'): return "BOBBIO PELLICE"
    elif t.startswith('Pt'): return "PONT SAINT MARTIN"
    elif t.startswith('Iv'): return "IVREA"
    elif t.startswith('Su'): return "SUSA"
    elif t.startswith('Sa'): return "SALBERTRAND"
    elif t.startswith('Ca'): return "CASELLE"
    elif t.startswith('Pb'): return "PIOBESI"
    return "ALTRO"

turni_list = []
for r in rows[1:]:
    if r and r[0].strip():
        turni_list.append(r[0].strip())

# Calcoliamo il riepilogo depositi
conteggio_depositi = Counter([ricava_deposito(t) for t in turni_list])

print("Riepilogo Turni per Deposito:")
for d, count in sorted(conteggio_depositi.items()):
    print(f"  - {d:<20}: {count} turni")

# Ricostruiamo il foglio in modo pulito senza formule esterne rotte
nuove_righe = [
    ["Codice Turno", "Deposito Reale", "", "Riepilogo Depositi", "Totale Turni"]
]

depositi_ordinati = sorted(conteggio_depositi.items())
max_len = max(len(turni_list), len(depositi_ordinati))

for i in range(max_len):
    t_code = turni_list[i] if i < len(turni_list) else ""
    t_dep = ricava_deposito(t_code) if t_code else ""
    
    rep_dep = depositi_ordinati[i][0] if i < len(depositi_ordinati) else ""
    rep_tot = depositi_ordinati[i][1] if i < len(depositi_ordinati) else ""
    
    nuove_righe.append([t_code, t_dep, "", rep_dep, rep_tot])

# Aggiorniamo le prime 5 colonne del foglio
ws_nt.update('A1:E' + str(len(nuove_righe)), nuove_righe)
print(f"✅ Foglio 'Numero turni' riparato con successo senza errori #ERROR!!")
