import gspread
from oauth2client.service_account import ServiceAccountCredentials
url = 'https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777'
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
ws = client.open_by_url(url).worksheet('Tabella Turni scol 2026')
data = ws.get_all_values()

shifts = [r[0].strip() for r in data if r]
print("First 10 shifts:")
print(shifts[:10])

# Find where the special codes start
for i, s in enumerate(shifts):
    if s == 'DISP':
        print(f"DISP is at index {i}")

