import fitz
import re
import glob
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_riprese(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    # 04, 05, etc. are aligned horizontally. We find the X coord of the FIRST hour printed, and what hour it is.
    words = page.get_text('words')
    first_hour_x = 9999
    first_hour_val = 5
    for w in words:
        if 30 < w[1] < 45 and w[4].isdigit() and len(w[4]) == 2:
            if w[0] < first_hour_x:
                first_hour_x = w[0]
                first_hour_val = int(w[4])
    
    if first_hour_x == 9999:
        first_hour_x = 76.56 # fallback
        
    pixels_per_min = 39.0 / 60.0
    
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
            current_shift = {'name': text, 'y0': y0, 'y1': y1}
            continue
        if current_shift:
            current_shift['y1'] = y1
    if current_shift:
        shifts.append(current_shift)
        
    drawings = page.get_drawings()
    
    results = {}
    for i in range(len(shifts)):
        s_y0 = shifts[i]['y0']
        s_y1 = shifts[i+1]['y0'] if i + 1 < len(shifts) else s_y0 + 25
        shift_name = shifts[i]['name']
        
        # Get grey bars
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
                    
        formatted = [(f"{int(s//60):02d}.{int(s%60):02d}", f"{int(e//60):02d}.{int(e%60):02d}") for s, e in merged]
        results[shift_name] = formatted
    return results

def main():
    url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_url(url)
    ws = spreadsheet.worksheet('Tabella Turni scol 2026')
    
    all_riprese = {}
    pdfs = glob.glob('Turni settembre 2026/Crew_Graph__*.pdf')
    for pdf in pdfs:
        print(f"Estraendo riprese da {pdf}...")
        all_riprese.update(get_riprese(pdf))
        
    print(f"Trovati {len(all_riprese)} turni in totale.")
    
    data = ws.get_all_values()
    updates = []
    
    for i, row in enumerate(data):
        if not row: continue
        t_name = row[0].strip()
        if not t_name: continue
        
        found_name = None
        if t_name in all_riprese:
            found_name = t_name
        elif t_name[:-1] in all_riprese and t_name.endswith('0'):
            found_name = t_name[:-1]
            
        if found_name:
            rips = all_riprese[found_name]
            print(f"Aggiornamento {t_name} (da {found_name}): {rips}")
            
            cols = [(5,6), (8,9), (11,12), (14,15), (17,18), (20,21)]
            
            for rip_idx in range(len(cols)):
                c_start, c_end = cols[rip_idx]
                cell_start = gspread.utils.rowcol_to_a1(i+1, c_start+1)
                cell_end = gspread.utils.rowcol_to_a1(i+1, c_end+1)
                
                if rip_idx < len(rips):
                    val_start = rips[rip_idx][0]
                    val_end = rips[rip_idx][1]
                    # We format as hh.mm 
                    updates.append({'range': cell_start, 'values': [[val_start]]})
                    updates.append({'range': cell_end, 'values': [[val_end]]})
                else:
                    updates.append({'range': cell_start, 'values': [['']]})
                    updates.append({'range': cell_end, 'values': [['']]})

    if updates:
        print(f"Eseguo {len(updates)} aggiornamenti sul foglio...")
        ws.batch_update(updates)
        print("Fatto!")
    else:
        print("Nessun turno da aggiornare.")

if __name__ == '__main__':
    main()
