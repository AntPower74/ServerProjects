import gspread
from oauth2client.service_account import ServiceAccountCredentials

url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=75866938#gid=75866938"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

try:
    spreadsheet = client.open_by_url(url)
    print(f"Spreadsheet Title: {spreadsheet.title}")
    print("Worksheets:")
    for ws in spreadsheet.worksheets():
        print(f" - {ws.title}")
        
    ws = spreadsheet.get_worksheet(0)
    print("\nSample Data from first worksheet:")
    for row in ws.get_all_values()[:10]:
        print(row)
except Exception as e:
    print(f"Error: {e}")
