import gspread
from oauth2client.service_account import ServiceAccountCredentials

url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url(url)
ws = spreadsheet.worksheet('Tabella Turni scol 2026')

# You can get validation rules via get_all_values if it's just values, but to see data validation we need the API response
req = spreadsheet.fetch_sheet_metadata({"includeGridData": True})
sheet_data = next(s for s in req['sheets'] if s['properties']['title'] == 'Tabella Turni scol 2026')
if 'data' in sheet_data and sheet_data['data']:
    grid_data = sheet_data['data'][0]
    if 'rowData' in grid_data:
        # Check row 2 (index 1), column H (index 7)
        row = grid_data['rowData'][1]
        if 'values' in row and len(row['values']) > 7:
            cell = row['values'][7]
            if 'dataValidation' in cell:
                print("Data Validation for H2:")
                print(cell['dataValidation'])
            else:
                print("No Data Validation on H2")

