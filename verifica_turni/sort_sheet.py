import gspread
from oauth2client.service_account import ServiceAccountCredentials

url = 'https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777'
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url(url)
ws = spreadsheet.worksheet('Tabella Turni scol 2026')
sheet_id = ws.id

data = ws.get_all_values()
shifts = [r[0].strip() if r else '' for r in data]

# Find DISP
try:
    disp_idx = shifts.index('DISP')
except ValueError:
    disp_idx = -1
    print("Could not find DISP")
    exit(1)
    
# Find RIP
try:
    rip_idx = shifts.index('RIP')
except ValueError:
    rip_idx = -1

# The appended rows are everything after RIP
last_shift_idx = len(shifts) - 1
while last_shift_idx > rip_idx and shifts[last_shift_idx] == '':
    last_shift_idx -= 1

print(f"DISP is at row {disp_idx+1}")
print(f"RIP is at row {rip_idx+1}")
print(f"Last appended shift is at row {last_shift_idx+1}")

appended_count = last_shift_idx - rip_idx

requests = []

if appended_count > 0:
    # 1. Move the appended rows from (rip_idx+1 ... last_shift_idx) to just before DISP (disp_idx)
    move_request = {
        "moveDimension": {
            "source": {
                "sheetId": sheet_id,
                "dimension": "ROWS",
                "startIndex": rip_idx + 1,
                "endIndex": last_shift_idx + 1
            },
            "destinationIndex": disp_idx
        }
    }
    requests.append(move_request)
    
    # After moving, the block of shifts to sort will be from row 1 (0-indexed) to disp_idx + appended_count
    sort_end_index = disp_idx + appended_count
else:
    sort_end_index = disp_idx
    
# 2. Sort the rows from index 1 (row 2) to sort_end_index
sort_request = {
    "sortRange": {
        "range": {
            "sheetId": sheet_id,
            "startRowIndex": 1,
            "endRowIndex": sort_end_index,
            "startColumnIndex": 0,
            "endColumnIndex": len(data[0]) # up to the last column
        },
        "sortSpecs": [
            {
                "dimensionIndex": 0, # Sort by Column A
                "sortOrder": "ASCENDING"
            }
        ]
    }
}
requests.append(sort_request)

res = spreadsheet.batch_update({"requests": requests})
print("Move and Sort applied successfully!")

