import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def main():
    with open('exact_shift_times.json') as f:
        all_shifts = json.load(f)
    
    url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    ws = client.open_by_url(url).worksheet('Tabella Turni scol 2026')
    data = ws.get_all_values()
    
    # F=5,G=6 | I=8,J=9 | L=11,M=12 | O=14,P=15 | R=17,S=18 | U=20,V=21
    rip_cols = [(5,6), (8,9), (11,12), (14,15), (17,18), (20,21)]
    
    updates = []
    applied = []
    
    for i, row in enumerate(data):
        if not row: continue
        t_name = row[0].strip()
        if t_name not in all_shifts: continue
        
        rips = all_shifts[t_name]  # NO tempi accessori - already in cartellino
        applied.append(t_name)
        
        for rip_idx in range(len(rip_cols)):
            c_start, c_end = rip_cols[rip_idx]
            cell_start = gspread.utils.rowcol_to_a1(i+1, c_start+1)
            cell_end   = gspread.utils.rowcol_to_a1(i+1, c_end+1)
            
            if rip_idx < len(rips):
                updates.append({'range': cell_start, 'values': [[rips[rip_idx][0]]]})
                updates.append({'range': cell_end,   'values': [[rips[rip_idx][1]]]})
            else:
                updates.append({'range': cell_start, 'values': [['']]})
                updates.append({'range': cell_end,   'values': [['']]})
    
    print(f"Updating {len(applied)} shifts (WITHOUT tempi accessori)...")
    batch_size = 500
    for i in range(0, len(updates), batch_size):
        ws.batch_update(updates[i:i+batch_size])
        print(f"  Batch {i//batch_size + 1} done")
    print("Done!")

if __name__ == '__main__':
    main()
