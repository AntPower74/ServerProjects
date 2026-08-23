import gspread
from oauth2client.service_account import ServiceAccountCredentials
url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url(url)
ws = None
for w in spreadsheet.worksheets():
    if w.id == 715797777:
        ws = w
        break

if ws:
    data = ws.get_all_values()
    for row in data:
        if 'To0720' in row[0] or 'Tocomm' in row[0] or 'To0640' in row[0]:
            print(row[:20])
