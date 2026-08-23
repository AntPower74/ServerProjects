import gspread
from oauth2client.service_account import ServiceAccountCredentials

url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url(url)
ws = spreadsheet.worksheet('Tabella Turni scol 2026')
# wait, it might be in Tabella Turni scol 2026
req = spreadsheet.fetch_sheet_metadata({"includeGridData": True})
sheet_data = next(s for s in req['sheets'] if s['properties']['title'] == 'Tabella Turni scol 2026')
grid_data = sheet_data['data'][0]
found = False
for i, row in enumerate(grid_data.get('rowData', [])):
    if i == 23: # Row 24 (0-indexed 23)
        if 'values' in row:
            for j, cell in enumerate(row['values']):
                if 'userEnteredValue' in cell and 'formulaValue' in cell['userEnteredValue']:
                    form = cell['userEnteredValue']['formulaValue']
                    if 'Competenze' in form:
                        print(f"Found formula in Column {j} (Row 24): {form}")
                        found = True
if not found:
    print("Formula not found in row 24 of Tabella Turni scol 2026")
