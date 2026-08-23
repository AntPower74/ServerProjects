import gspread
from oauth2client.service_account import ServiceAccountCredentials

url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
ws = client.open_by_url(url).worksheet('Tabella Turni scol 2026')

data = ws.get_all_values()
for i, row in enumerate(data):
    if row[0].strip() == 'Lu0020':
        print(f"Lu0020 row {i+1}:")
        print("F (Inizio 1):", row[5] if len(row) > 5 else '')
        print("G (Fine 1):", row[6] if len(row) > 6 else '')
        print("I (Inizio 2):", row[8] if len(row) > 8 else '')
        print("J (Fine 2):", row[9] if len(row) > 9 else '')
        print("L (Inizio 3):", row[11] if len(row) > 11 else '')
        print("M (Fine 3):", row[12] if len(row) > 12 else '')
        break
        
    if row[0].strip() == 'Pe0190':
        print(f"Pe0190 row {i+1}:")
        print("F (Inizio 1):", row[5] if len(row) > 5 else '')
        break
