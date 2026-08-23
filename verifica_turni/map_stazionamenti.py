import gspread
from oauth2client.service_account import ServiceAccountCredentials
import difflib

url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
ws = client.open_by_url(url).worksheet('Stazionamenti')

data = ws.col_values(1)
valid_locations = [x.strip() for x in data if x.strip()]
print("Found", len(valid_locations), "valid locations.")

# Test a few matches
test_strings = [
    "Luserna S.Giovanni Deposito",
    "Pinerolo Piazza Cavour",
    "Airasca stabilimento sk",
    "Torino Via Borsellino (PARK)",
    "Pinerolo Movicentro",
    "TORINO Autostazione c.s",
    "Perosa Deposito"
]

for t in test_strings:
    # use difflib to find closest match
    matches = difflib.get_close_matches(t, valid_locations, n=1, cutoff=0.3)
    if matches:
        print(f"'{t}' -> '{matches[0]}'")
    else:
        print(f"'{t}' -> NO MATCH")

