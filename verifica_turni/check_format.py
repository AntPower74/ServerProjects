import gspread
from oauth2client.service_account import ServiceAccountCredentials

url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url(url)
ws = spreadsheet.worksheet('Tabella Turni scol 2026')

req = spreadsheet.fetch_sheet_metadata({"includeGridData": True})
sheet_data = next(s for s in req['sheets'] if s['properties']['title'] == 'Tabella Turni scol 2026')
grid_data = sheet_data['data'][0]
row24 = grid_data['rowData'][23] # index 23 is row 24

# F24 is index 5
cell_f24 = row24['values'][5]
cell_g24 = row24['values'][6]
cell_w24 = row24['values'][22] # W is 22

print("F24 raw:", cell_f24)
print("G24 raw:", cell_g24)
print("W24 raw:", cell_w24)

# Print AB24 (index 27) and AC24 (index 28) and AD24 (index 29)
print("AB24:", row24['values'][27].get('formattedValue'))
print("AC24:", row24['values'][28].get('formattedValue'))
print("AD24:", row24['values'][29].get('formattedValue'))
