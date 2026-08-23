import gspread
from oauth2client.service_account import ServiceAccountCredentials
url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
ws = client.open_by_url(url).worksheet('Tabella Turni scol 2026')
data = ws.get_all_values()
print(f"Total rows in sheet: {len(data)}")
for i, row in enumerate(data):
    if i > len(data) - 45:
        print(f"Row {i+1}: {row[0]}")
