import json
import gspread
from google.oauth2.service_account import Credentials
from collections import defaultdict

SPREADSHEET_ID = "1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM"
creds_path = "/home/antonio/verifica_turni/credentials.json"

scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials = Credentials.from_service_account_file(creds_path, scopes=scopes)
gc = gspread.authorize(credentials)
sh = gc.open_by_key(SPREADSHEET_ID)

ws_corse = sh.worksheet("Corse per turno")
rows = ws_corse.get_all_values()

db_corse = defaultdict(list)

for r in rows[1:]:
    if len(r) >= 9 and r[8].strip():
        turno = r[8].strip()
        db_corse[turno].append({
            'corsa_id': r[0],
            'cod_corsa': r[1],
            'cod_linea': r[2],
            'partenza': r[3],
            'ora_partenza': r[4],
            'arrivo': r[5],
            'ora_arrivo': r[6],
            'spezzata': r[7]
        })

with open("/home/antonio/verifica_turni/DATABASE_CORSE_DA_SHEETS.json", "w", encoding="utf-8") as f:
    json.dump(db_corse, f, indent=2, ensure_ascii=False)

print(f"✅ Salvato database locale: {len(db_corse)} turni con le relative corse dettagliate!")
