import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url(url)
ws = spreadsheet.worksheet('Tabella Turni scol 2026')
ws_valid = spreadsheet.worksheet('Stazionamenti')

valid_locs = [x.strip() for x in ws_valid.col_values(1) if x.strip()]
valid_lower = {v.lower(): v for v in valid_locs}

def map_location(raw):
    r_lower = raw.lower()
    
    # Check exact substring match
    for v_lower, v_real in valid_lower.items():
        if v_lower in r_lower:
            return v_real
            
    # Special rules
    if r_lower.startswith('to ') or r_lower.startswith('to-'):
        return 'Torino'
    if 'pont s' in r_lower or 'pont st' in r_lower:
        return 'Pont S. Martin'
        
    # If no match, return original (or empty?)
    # Returning empty would clear the cell, but maybe we leave it as is if we can't map it.
    return None

data = ws.get_all_values()
sosta_cols = [7, 10, 13, 16, 19] # H, K, N, Q, T

updates = []

for i, row in enumerate(data):
    if i == 0: continue
    
    for c in sosta_cols:
        if c < len(row) and row[c].strip():
            current_val = row[c].strip()
            if current_val not in valid_locs:
                mapped = map_location(current_val)
                if mapped:
                    cell = gspread.utils.rowcol_to_a1(i+1, c+1)
                    updates.append({'range': cell, 'values': [[mapped]]})
                    print(f"Mapping '{current_val}' -> '{mapped}' at {cell}")
                    
if updates:
    ws.batch_update(updates)
    print(f"Fixed {len(updates)} cells!")
else:
    print("No cells needed fixing.")

