import gspread
from oauth2client.service_account import ServiceAccountCredentials

url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
ws = client.open_by_url(url).worksheet('Tabella Turni scol 2026')

# Delete rows from 258 to 335 (index 258 to 335 inclusive)
# gspread delete_rows takes start_index and end_index (1-based)
ws.delete_rows(258, 335)
print("Deleted rows 258 to 335")
