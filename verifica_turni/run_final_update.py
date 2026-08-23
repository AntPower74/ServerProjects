import fitz
import re
import glob
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
                current_shift = {'name': text, 'y0': y0, 'y1': y1}
                continue
            if current_shift:
                current_shift['y1'] = y1
        if current_shift:
            shifts.append(current_shift)
            
        drawings = page.get_drawings()
        
        for i in range(len(shifts)):
            s_y0 = shifts[i]['y0']
            s_y1 = shifts[i+1]['y0'] if i + 1 < len(shifts) else s_y0 + 25
            shift_name = shifts[i]['name']
            
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


def map_shift_name(pdf_name, sheet_names_lower_map):
    p_lower = pdf_name.lower()
    if p_lower in sheet_names_lower_map:
        return sheet_names_lower_map[p_lower]
        
    if (p_lower + '0') in sheet_names_lower_map:
        return sheet_names_lower_map[p_lower + '0']
        
    m = re.match(r'^([a-zA-Z]+)(0*\d+)$', pdf_name)
    if m:
        prefix = m.group(1).capitalize()
        num = int(m.group(2))
        guess = f"{prefix}{num:03d}0"
        if guess.lower() in sheet_names_lower_map:
            return sheet_names_lower_map[guess.lower()]
        return guess
        
    return pdf_name.capitalize()

def main():
    url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    ws = client.open_by_url(url).worksheet('Tabella Turni scol 2026')
    
    data = ws.get_all_values()
    sheet_names_lower_map = {}
    for row in data:
        if row:
            t = row[0].strip()
            if t: 
                sheet_names_lower_map[t.lower()] = t
                
    all_riprese = {}
    pdfs = glob.glob('Turni settembre 2026/Crew_Graph__*.pdf')
    for pdf in pdfs:
        for k, v in get_riprese(pdf).items():
            norm_name = map_shift_name(k, sheet_names_lower_map)
            all_riprese[norm_name] = v
            
    # Now we know all_riprese has keys matching the sheet exactly if they exist.
    missing_names = []
    for k in all_riprese.keys():
        if k.lower() not in sheet_names_lower_map:
            missing_names.append(k)
            
    print(f"Turni totali estratti: {len(all_riprese)}")
    print(f"Turni mancanti che verranno aggiunti in fondo: {len(missing_names)}")
    print(missing_names)
    
    # 1. Update existing
    updates = []
    for i, row in enumerate(data):
        if not row: continue
        t_name = row[0].strip()
        if t_name in all_riprese:
            rips = all_riprese[t_name]
            cols = [(5,6), (8,9), (11,12), (14,15), (17,18), (20,21)]
            for rip_idx in range(len(cols)):
                c_start, c_end = cols[rip_idx]
                cell_start = gspread.utils.rowcol_to_a1(i+1, c_start+1)
                cell_end = gspread.utils.rowcol_to_a1(i+1, c_end+1)
                if rip_idx < len(rips):
                    updates.append({'range': cell_start, 'values': [[rips[rip_idx][0]]]})
                    updates.append({'range': cell_end, 'values': [[rips[rip_idx][1]]]})
                else:
                    updates.append({'range': cell_start, 'values': [['']]})
                    updates.append({'range': cell_end, 'values': [['']]})
                    
    if updates:
        ws.batch_update(updates)
        print("Aggiornamento turni esistenti completato.")

    # 2. Append missing
    if missing_names:
        new_rows = []
        for m_name in missing_names:
            rips = all_riprese[m_name]
            row = [m_name, '', '', '', '']
            for _ in range(17):
                row.append('')
            
            cols = [(5,6), (8,9), (11,12), (14,15), (17,18), (20,21)]
            for rip_idx in range(min(len(rips), len(cols))):
                c_start, c_end = cols[rip_idx]
                row[c_start] = rips[rip_idx][0]
                row[c_end] = rips[rip_idx][1]
            
            new_rows.append(row)
            
        ws.append_rows(new_rows, value_input_option='USER_ENTERED')
        print(f"Aggiunti {len(new_rows)} nuovi turni in fondo al foglio.")

if __name__ == '__main__':
    main()
