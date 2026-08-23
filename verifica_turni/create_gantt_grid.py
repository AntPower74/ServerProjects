import gspread
from oauth2client.service_account import ServiceAccountCredentials
import math

url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url(url)

# Get source data
ws_source = None
for w in spreadsheet.worksheets():
    if w.title == 'Tabella Turni':
        ws_source = w
        break

data = ws_source.get_all_values()

# Create or get target worksheet
try:
    ws_target = spreadsheet.worksheet('Grafico Copertura (Gantt)')
    ws_target.clear()
except gspread.exceptions.WorksheetNotFound:
    ws_target = spreadsheet.add_worksheet(title='Grafico Copertura (Gantt)', rows="500", cols="60")

def parse_time_to_mins(t_str):
    if not t_str or t_str.strip() == '':
        return None
    try:
        t_str = t_str.replace(',', '.')
        parts = t_str.split('.')
        h = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 0
        
        mins = h * 60 + m
        # Se l'orario è tra le 00:00 e le 03:59, lo consideriamo del giorno dopo (+24h)
        if mins < 4 * 60:
            mins += 24 * 60
        return mins
    except:
        return None

# Generate headers (every 30 mins from 04:00 to 27:30)
headers = ["Turno", "Residenza"]
intervals = []
for h in range(4, 28):
    for m in [0, 30]:
        display_h = h if h < 24 else h - 24
        headers.append(f"{display_h:02d}:{m:02d}")
        intervals.append(h * 60 + m)

output_data = [headers]

for row in data[1:]:
    turno = row[0]
    if not turno: continue
    residenza = row[3] if len(row) > 3 else ""
    
    # Extract start/end pairs
    # Inizio 1: col 5, Fine 1: col 6
    # Inizio 2: col 8, Fine 2: col 9
    # Inizio 3: col 11, Fine 3: col 12
    # Inizio 4: col 14, Fine 4: col 15
    # Inizio 5: col 17, Fine 5: col 18
    # Inizio 6: col 20, Fine 6: col 21
    
    active_periods = []
    
    col_pairs = [(5,6), (8,9), (11,12), (14,15), (17,18), (20,21)]
    for start_col, end_col in col_pairs:
        if len(row) > end_col:
            start_m = parse_time_to_mins(row[start_col])
            end_m = parse_time_to_mins(row[end_col])
            
            if start_m is not None and end_m is not None:
                # Gestione caso in cui end è minore di start (cavallo mezzanotte ma parsing fallito)
                if end_m < start_m:
                    end_m += 24*60
                active_periods.append((start_m, end_m))
                
    if not active_periods:
        continue
        
    out_row = [turno, residenza]
    for interval_start in intervals:
        interval_end = interval_start + 30
        
        is_active = False
        for s, e in active_periods:
            # Check overlap
            if s < interval_end and e > interval_start:
                is_active = True
                break
        
        out_row.append(1 if is_active else "")
        
    output_data.append(out_row)

# Add Total Row
total_row = ["TOTALE AUTISTI", ""]
for i in range(2, len(headers)):
    col_letter = gspread.utils.rowcol_to_a1(1, i+1).replace('1', '')
    total_row.append(f"=SUM({col_letter}2:{col_letter}{len(output_data)})")
    
output_data.append(total_row)

print("Updating sheet...")
ws_target.update(range_name='A1', values=output_data, value_input_option='USER_ENTERED')

# Format the sheet
# We would ideally color cells with '1' but it's hard to do conditionally via basic update.
# We will just write the numbers, user can add conditional formatting easily.
print("Done!")
