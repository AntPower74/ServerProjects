import gspread
from oauth2client.service_account import ServiceAccountCredentials
url = "https://docs.google.com/spreadsheets/d/1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM/edit?gid=1405846221#gid=1405846221"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url(url)
print("Worksheets:")
for w in spreadsheet.worksheets():
    print(w.title)
