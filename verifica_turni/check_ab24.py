import gspread
from oauth2client.service_account import ServiceAccountCredentials

url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url(url)
ws = spreadsheet.worksheet('Tabella Turni scol 2026')

val = ws.acell('AB24').value
val_formula = ws.acell('AB24', value_render_option='FORMULA').value
print(f"AB24 value: {val}")
print(f"AB24 formula: {val_formula}")

# also print the header for AB
header_ab = ws.acell('AB1').value
print(f"Header for AB: {header_ab}")
