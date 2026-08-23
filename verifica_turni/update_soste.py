import fitz
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def extract_break_locations(pdfs, target_shift, break_times):
    # Try all pdfs until found
    for pdf_path in pdfs:
        doc = fitz.open(pdf_path)
        for page in doc:
            text = page.get_text()
            if target_shift in text:
                words = page.get_text('words')
                locations = {}
                for target_time in break_times:
                    # Time in Cartellini might be formatted with ':' 
                    # but in Tabella Turni scol 2026 we used '.' previously
                    # Wait, we just applied tempi accessori and changed them to '.'
                    # But the break time is the ORIGINAL time, without tempi accessori!
                    # Ah! For the break start, it is Fine X. Fine X is NOT the last fine.
                    # Wait, the tempi accessori ONLY apply to the FIRST INIZIO and LAST FINE.
                    # So the intermediate Fine times are UNCHANGED and match the PDF exactly!
                    # However, they are stored with '.' in Tabella Turni, but Cartellini uses ':'
                    
                    search_time = target_time.replace('.', ':')
                    time_words = [w for w in words if search_time in w[4]]
                    if not time_words:
                        continue
                    
                    for tw in time_words:
                        y_time = tw[1]
                        x_time = tw[0]
                        
                        loc_words = [w for w in words if abs(w[1] - y_time) < 5 and (x_time - 160) < w[0] < x_time]
                        loc_words.sort(key=lambda w: w[0])
                        
                        clean_loc = []
                        for lw in loc_words:
                            if re.match(r'^\d{2}:\d{2}$', lw[4]): continue
                            if 'ID' in lw[4] or 'corsa' in lw[4] or 'Linea' in lw[4] or '|' in lw[4]: continue
                            if re.match(r'^\d+$', lw[4]): continue
                            if lw[4] == '-': continue
                            clean_loc.append(lw[4])
                            
                        loc_str = " ".join(clean_loc).strip()
                        loc_str = re.sub(r'\.{3,}', '', loc_str).strip()
                        if loc_str and loc_str != "PAUSA":
                            locations[target_time] = loc_str
                            break
                return locations
    return {}

def map_shift_name_reverse(sheet_name):
    # Map 'Lu0010' back to 'Lu001' to search in Cartellini
    m = re.match(r'^([a-zA-Z]+)(\d+)(0)$', sheet_name)
    if m:
        prefix = m.group(1)
        num = int(m.group(2))
        return f"{prefix}{num:03d}"
    return sheet_name

def main():
    url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    ws = client.open_by_url(url).worksheet('Tabella Turni scol 2026')
    
    data = ws.get_all_values()
    
    cartellini_pdfs = [
        'Cartellini turni da settembre 2026.pdf',
        'cartellini scolastici torino attuali.pdf',
        'cartellini scolastici pinerolo attuali.pdf',
        'Turni dal 100925_giov.base scolastico.pdf'
    ]
    
    updates = []
    
    # Columns for Fine X: 6 (G), 9 (J), 12 (M), 15 (P), 18 (S)
    # Corresponding Sosta columns: 7 (H), 10 (K), 13 (N), 16 (Q), 19 (T)
    fine_cols = [6, 9, 12, 15, 18]
    sosta_cols = [7, 10, 13, 16, 19]
    
    for i, row in enumerate(data):
        if not row: continue
        if i == 0: continue # Header
        
        t_name = row[0].strip()
        if not t_name or t_name in ['DISP', 'BIS', 'NOL', 'ACM', 'ACV', 'ADS', 'AF', 'AI', 'AM', 'APMAF', 'APMAT', 'APNRO', 'APR', 'AREC', 'AS', 'AST', 'ASL', 'GL', 'RC', 'RF', 'FBS', 'RIP']:
            continue
            
        search_name = map_shift_name_reverse(t_name)
        
        # Find all Fine X times that are followed by an Inizio X+1
        # (This means it's a break)
        breaks_to_find = []
        for c_idx in range(len(fine_cols)):
            fine_col = fine_cols[c_idx]
            if fine_col < len(row) and row[fine_col].strip():
                # Check if there is a next Inizio (which is fine_col + 2)
                next_inizio_col = fine_col + 2
                if next_inizio_col < len(row) and row[next_inizio_col].strip():
                    breaks_to_find.append((row[fine_col].strip(), sosta_cols[c_idx]))
                    
        if breaks_to_find:
            break_times = [b[0] for b in breaks_to_find]
            locs = extract_break_locations(cartellini_pdfs, search_name, break_times)
            
            for b_time, s_col in breaks_to_find:
                if b_time in locs:
                    cell = gspread.utils.rowcol_to_a1(i+1, s_col+1)
                    updates.append({'range': cell, 'values': [[locs[b_time]]]})
                    print(f"{t_name} break at {b_time} -> {locs[b_time]} (Cell {cell})")
                    
    if updates:
        ws.batch_update(updates)
        print(f"Updated {len(updates)} Sosta locations successfully!")

if __name__ == '__main__':
    main()
