import fitz
import re
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def extract_break_location_optibus(page, break_time_dot):
    """For Optibus-format cartellini: look up location at break time (using ':' format)"""
    search_time = break_time_dot.replace('.', ':')
    words = page.get_text('words')
    
    time_words = [w for w in words if search_time in w[4]]
    if not time_words:
        return None
    
    for tw in time_words:
        y_time = tw[1]
        x_time = tw[0]
        
        # location words are on the same Y, to the LEFT of the time
        loc_words = [w for w in words if abs(w[1] - y_time) < 5 and (x_time - 160) < w[0] < x_time]
        loc_words.sort(key=lambda w: w[0])
        
        clean_loc = []
        for lw in loc_words:
            if re.match(r'^\d{2}:\d{2}$', lw[4]): continue
            if any(k in lw[4] for k in ['ID', 'corsa', 'Linea', '|']): continue
            if re.match(r'^\d+$', lw[4]): continue
            if lw[4] == '-': continue
            clean_loc.append(lw[4])
        
        loc_str = ' '.join(clean_loc).strip()
        loc_str = re.sub(r'\.{3,}', '', loc_str).strip()
        if loc_str and loc_str != 'PAUSA':
            return loc_str
    
    return None

def extract_break_location_arriva(page, break_time_dot):
    """For ARRIVA-format cartellini: find location at break F.Ripresa time"""
    # In ARRIVA format, times use dots too (e.g., '5.30')
    # Normalize: '05.30' -> '5.30' might be needed
    search_dot = break_time_dot.lstrip('0') if break_time_dot[0] == '0' else break_time_dot
    # also try zero-padded
    search_dot2 = break_time_dot
    
    words = page.get_text('words')
    words.sort(key=lambda w: (w[1], w[0]))
    
    for search in [search_dot, search_dot2]:
        time_words = [w for w in words if w[4] == search]
        for tw in time_words:
            y = tw[1]
            # In ARRIVA format, the location/description is in the same row
            row_words = [w for w in words if abs(w[1] - y) < 4]
            row_words.sort(key=lambda w: w[0])
            
            # Description is between the line number (3-digit) and the times
            desc_words = []
            found_line_no = False
            for rw in row_words:
                if re.match(r'^\d{6}$', rw[4]):  # 6-digit corsa ID
                    found_line_no = True
                    continue
                if found_line_no:
                    if re.match(r'^\d{1,2}\.\d{2}$', rw[4]):  # hit a time, stop
                        break
                    if re.match(r'^\d+$', rw[4]): continue  # skip numbers
                    desc_words.append(rw[4])
            
            if desc_words:
                desc = ' '.join(desc_words).strip()
                # Extract location: typically the last "place name" before the first '-'
                return desc
    
    return None

def map_location(raw, valid_locs):
    if not raw: return None
    r_lower = raw.lower()
    valid_lower = {v.lower(): v for v in valid_locs}
    
    # Exact substring match
    for v_lower, v_real in valid_lower.items():
        if v_lower in r_lower:
            return v_real
    
    # Special rules
    if r_lower.startswith('to ') or r_lower.startswith('to-') or 'torino' in r_lower:
        return 'Torino'
    if 'pont s' in r_lower or 'pont st' in r_lower:
        return 'Pont S. Martin'
    if 'caselle' in r_lower:
        return 'Caselle'
    if 'pinerolo' in r_lower or 'movicentro' in r_lower:
        return 'Pinerolo'
    if 'luserna' in r_lower:
        return 'Luserna'
    
    return None

def main():
    url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_url(url)
    ws = spreadsheet.worksheet('Tabella Turni scol 2026')
    ws_valid = spreadsheet.worksheet('Stazionamenti')
    
    valid_locs = [x.strip() for x in ws_valid.col_values(1) if x.strip()]
    data = ws.get_all_values()
    
    # Build lookup: shift_name -> page object (for fast search)
    # Optibus PDF: shift names like Lu001, Pe008 (3 digits)
    # ARRIVA PDFs: shift names like Lu0010, To0260 (4 digits)
    optibus_pages = {}  # norm_name -> page
    arriva_pages = {}   # norm_name -> page

    doc_opt = fitz.open('Cartellini turni da settembre 2026.pdf')
    for page in doc_opt:
        words = page.get_text('words')
        for w in words:
            if re.match(r'^[A-Z][a-z]\d{3}$', w[4]) and w[1] < 100:
                m = re.match(r'^([A-Z][a-z])(\d+)$', w[4])
                if m:
                    norm = f"{m.group(1)}{int(m.group(2)):03d}0"
                    optibus_pages[norm] = page
                break

    for pdf in ['cartellini scolastici torino attuali.pdf', 'cartellini scolastici pinerolo attuali.pdf']:
        doc = fitz.open(pdf)
        for page in doc:
            words = page.get_text('words')
            for w in words:
                if re.match(r'^[A-Z][a-z]\d{4}$', w[4]) and w[1] < 50:
                    arriva_pages[w[4]] = page
                    break

    # Fine columns (0-indexed): G=6, J=9, M=12, P=15, S=18
    # Sosta columns (0-indexed): H=7, K=10, N=13, Q=16, T=19
    # Next Inizio (0-indexed): I=8, L=11, O=14, R=17, U=20
    fine_cols  = [6, 9, 12, 15, 18]
    sosta_cols = [7, 10, 13, 16, 19]
    next_ini   = [8, 11, 14, 17, 20]
    
    skip = {'DISP','BIS','NOL','ACM','ACV','ADS','AF','AI','AM','APMAF','APMAT',
            'APNRO','APR','AREC','AS','AST','ASL','GL','RC','RF','FBS','RIP',''}
    
    updates = []
    
    for i, row in enumerate(data):
        if not row or i == 0: continue
        t_name = row[0].strip()
        if t_name in skip or not t_name: continue
        
        # Determine which PDF format this shift is in
        is_optibus = t_name in optibus_pages
        is_arriva  = t_name in arriva_pages
        
        if not is_optibus and not is_arriva:
            continue
        
        page = optibus_pages[t_name] if is_optibus else arriva_pages[t_name]
        
        for c_idx in range(len(fine_cols)):
            fine_col = fine_cols[c_idx]
            sosta_col = sosta_cols[c_idx]
            next_ini_col = next_ini[c_idx]
            
            if fine_col >= len(row) or not row[fine_col].strip():
                continue
            if next_ini_col >= len(row) or not row[next_ini_col].strip():
                continue  # Not a real break - last ripresa
            
            break_time = row[fine_col].strip()
            
            if is_optibus:
                loc_raw = extract_break_location_optibus(page, break_time)
            else:
                loc_raw = extract_break_location_arriva(page, break_time)
            
            if loc_raw:
                loc_mapped = map_location(loc_raw, valid_locs)
                if loc_mapped:
                    cell = gspread.utils.rowcol_to_a1(i+1, sosta_col+1)
                    updates.append({'range': cell, 'values': [[loc_mapped]]})
                    print(f"{t_name} stacco {break_time} -> {loc_raw[:30]} -> {loc_mapped} ({cell})")
    
    if updates:
        batch_size = 500
        for i in range(0, len(updates), batch_size):
            ws.batch_update(updates[i:i+batch_size])
        print(f"\nUpdated {len(updates)} Sosta locations!")
    else:
        print("No updates found.")

if __name__ == '__main__':
    main()
