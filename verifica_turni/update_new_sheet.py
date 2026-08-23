import fitz
import re
import glob
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def get_riprese(pdf_path):
    doc = fitz.open(pdf_path)
    results = {}
    pixels_per_min = 39.0 / 60.0
    
    for page in doc:
        words = page.get_text('words')
        first_hour_x = 9999
        first_hour_val = 5
        for w in words:
            if 30 < w[1] < 45 and w[4].isdigit() and len(w[4]) == 2:
                if w[0] < first_hour_x:
                    first_hour_x = w[0]
                    first_hour_val = int(w[4])
        
        if first_hour_x == 9999:
            first_hour_x = 76.56
            
        blocks = page.get_text('blocks')
        blocks = sorted(blocks, key=lambda b: b[1])
        
        shifts = []
        current_shift = None
        for b in blocks:
            x0, y0, x1, y1, text, block_no, block_type = b
            text = text.strip()
            if x0 < 30 and not text.startswith('(') and len(text) >= 2 and 'Crew Graph' not in text and 'Service:' not in text:
                if current_shift:
                    shifts.append(current_shift)
                current_shift = {'name': text, 'y0': y0, 'y1': y1, 'ore': ''}
                continue
            elif current_shift and text.startswith('(') and text.endswith(')'):
                current_shift['ore'] = text[1:-1] # remove parens
                
            if current_shift:
                current_shift['y1'] = y1
        if current_shift:
            shifts.append(current_shift)
            
        drawings = page.get_drawings()
        
        for i in range(len(shifts)):
            s_y0 = shifts[i]['y0']
            s_y1 = shifts[i+1]['y0'] if i + 1 < len(shifts) else s_y0 + 25
            shift_name = shifts[i]['name']
            ore = shifts[i]['ore']
            
            grey_bars = []
            for d in drawings:
                rect = d['rect']
                if s_y0 < rect.y0 < s_y1 and rect.height > 2 and rect.width > 20:
                    color = d.get('fill')
                    if color and len(color) == 3 and 0.5 < color[0] < 0.9 and abs(color[0]-color[1]) < 0.01:
                        start_mins = first_hour_val * 60 + (rect.x0 - first_hour_x) / pixels_per_min
                        end_mins = first_hour_val * 60 + (rect.x1 - first_hour_x) / pixels_per_min
                        grey_bars.append((start_mins, end_mins))
                        
            grey_bars.sort()
            
            time_points = []
            for w in words:
                w_x0, w_y0, w_x1, w_y1, w_text, _, _, _ = w
                if s_y0 - 2 <= w_y0 <= s_y1 - 2:
                    clean_t = re.sub(r'(.)\1{2}', r'\1', w_text)
                    if re.match(r'^\d{2}$', clean_t):
                        label_min = int(clean_t)
                        predicted_mins = first_hour_val * 60 + (w_x0 - first_hour_x) / pixels_per_min
                        best_h = -1
                        min_diff = 9999
                        for h in range(0, 28):
                            diff = abs((h * 60 + label_min) - predicted_mins)
                            if diff < min_diff:
                                min_diff = diff
                                best_h = h
                        if min_diff < 30:
                            time_points.append(best_h * 60 + label_min)
                            
            for b in blocks:
                x0, y0, x1, y1, text, block_no, block_type = b
                if s_y0 <= y0 <= s_y1:
                    clean_t = re.sub(r'(.)\1{2}', r'\1', text)
                    for line in clean_t.split('\n'):
                        m = re.search(r'(\d{2}):(\d{2})', line)
                        if m:
                            time_points.append(int(m.group(1))*60 + int(m.group(2)))
            
            time_points = sorted(list(set(time_points)))
            
            riprese = []
            for bar_s, bar_e in grey_bars:
                points_in_bar = [t for t in time_points if bar_s - 15 <= t <= bar_e + 15]
                if points_in_bar:
                    r_s = min(points_in_bar)
                    r_e = max(points_in_bar)
                else:
                    r_s = bar_s - 7
                    r_e = bar_e - 7
                riprese.append((r_s, r_e))
                
            merged = []
            for r in riprese:
                if not merged:
                    merged.append(r)
                else:
                    last_s, last_e = merged[-1]
                    curr_s, curr_e = r
                    if curr_s - last_e <= 30:
                        merged[-1] = (last_s, max(last_e, curr_e))
                    else:
                        merged.append(r)
                        
            # Format with COLON ':' instead of DOT '.'
            formatted = [(f"{int(s//60):02d}:{int(s%60):02d}", f"{int(e//60):02d}:{int(e%60):02d}") for s, e in merged]
            results[shift_name] = {'ore': ore, 'riprese': formatted}
    return results

def main():
    url = "https://docs.google.com/spreadsheets/d/1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM/edit?gid=1405846221#gid=1405846221"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_url(url)
    
    pdfs = glob.glob('Turni settembre 2026/Crew_Graph__*.pdf')
    for pdf in pdfs:
        tab_name = os.path.basename(pdf).replace('.pdf', '')
        
        try:
            ws = spreadsheet.worksheet(tab_name)
        except gspread.exceptions.WorksheetNotFound:
            print(f"Tab {tab_name} not found in sheet. Skipping.")
            continue
            
        print(f"Updating tab: {tab_name}")
        
        shifts_data = get_riprese(pdf)
        
        header = ['Nome Turno', 'Ore Pagate']
        for i in range(1, 7):
            header.append(f'Inizio {i}')
            header.append(f'Fine {i}')
            
        new_rows = [header]
        
        for s_name, data in shifts_data.items():
            row = [s_name, data['ore']]
            for r in data['riprese']:
                row.append(r[0])
                row.append(r[1])
            # Pad row to match header length
            while len(row) < len(header):
                row.append('')
            new_rows.append(row)
            
        # Clear sheet
        ws.clear()
        
        # Update sheet
        ws.update('A1', new_rows, value_input_option='USER_ENTERED')
        
        # Bold header
        ws.format('A1:N1', {'textFormat': {'bold': True}})
        
    print("All tabs updated successfully!")

if __name__ == '__main__':
    main()
