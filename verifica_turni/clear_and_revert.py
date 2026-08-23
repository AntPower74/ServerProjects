import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

print("Connecting to Google Sheets...")
url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
ws = client.open_by_key('1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM').worksheet('Tabella Turni scol 2025')
sheet_data = ws.get_all_values()

# Columns to clear: 1st to 6th Ripresa (Inizio, Fine, Sosta)
# F(5) to W(22)
cols_map = [
    (('F', 5), ('G', 6), ('H', 7)),
    (('I', 8), ('J', 9), ('K', 10)),
    (('L', 11), ('M', 12), ('N', 13)),
    (('O', 14), ('P', 15), ('Q', 16)),
    (('R', 17), ('S', 18), ('T', 19)),
    (('U', 20), ('V', 21), ('W', 22))
]

updates = []
print("Preparing to clear columns...")
for i, row in enumerate(sheet_data):
    if i == 0: continue
    
    # We clear the riprese and sosta columns for EVERY row
    for (s_col, _), (e_col, _), (sosta_col, _) in cols_map:
        updates.append({'range': f'{s_col}{i+1}', 'values': [['']]})
        updates.append({'range': f'{e_col}{i+1}', 'values': [['']]})
        updates.append({'range': f'{sosta_col}{i+1}', 'values': [['']]})

print(f"Total cells to clear: {len(updates)}")
batch_size = 200
for i in range(0, len(updates), batch_size):
    ws.batch_update(updates[i:i+batch_size])
print("Sheet cleared successfully!")
