import fitz
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_shift_info_from_page(page):
    words = page.get_text('words')
    lines = {}
    for w in words:
        if 25 < w[0] < 80 and w[1] > 65:
            y = round(w[1], 1)
            found = False
            for k in lines:
                if abs(k - y) < 4:
                    lines[k].append(w)
                    found = True
                    break
            if not found:
                lines[y] = [w]
    
    shift_names = {}
    for y, line_words in lines.items():
        line_words.sort(key=lambda x: x[0])
        name = "".join(w[4] for w in line_words).replace(" ","")
        if re.match(r'^[A-Z]{1,2}\d{1,4}[A-Z]?$', name) or re.match(r'^[A-Z][a-z]\d{1,4}[A-Z]?$', name):
            clean_name = re.sub(r'^\d+', '', name)
            shift_names[clean_name] = y
            
    return shift_names

def extract_minutes(text):
    if re.match(r'^\d{2}$', text): return [int(text)]
    if re.match(r'^\d{4}$', text): return [int(text[:2]), int(text[2:])]
    return []

def snap_time_advanced(graphical_mins, texts_with_x, target_x, is_start):
    gm = graphical_mins % 60
    gh = graphical_mins // 60
    
    valid_mins = []
    for x, t in texts_with_x:
        if abs(x - target_x) < 8:
            valid_mins.extend(extract_minutes(t))
            
    if not valid_mins:
        return graphical_mins
        
    candidate_times = []
    for m in valid_mins:
        diff = m - gm
        if diff > 30: diff -= 60
        elif diff < -30: diff += 60
        candidate_times.append(graphical_mins + diff)
        
    best_time = min(candidate_times) if is_start else max(candidate_times)
    
    if abs(best_time - graphical_mins) > 20:
        return graphical_mins
        
    return best_time

url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
ws = client.open_by_key('1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM').worksheet('Tabella Turni scol 2025')
data = ws.get_all_values()
valid_names = set(row[0].strip() for row in data[1:] if row[0].strip())

def pdf_name_to_sheet_name(pdf_name):
    if pdf_name in valid_names:
        return pdf_name
    m = re.match(r'^([A-Z][a-z])(\d+)$', pdf_name)
    if m:
        candidate = f"{m.group(1)}{int(m.group(2))*10:04d}"
        if candidate in valid_names:
            return candidate
    return None

def extract_all_crew_2025():
    pdfs = [
        'Turni settembre 2025/Turni dal 100925_giov.base scolastico.pdf',
        'Turni settembre 2025/Turni dal 130925_sabato scolastico.pdf',
        'Turni settembre 2025/Turni dal 140925_festivo invernale.pdf'
    ]
    all_shifts = {}
    
    for pdf_path in pdfs:
        doc = fitz.open(pdf_path)
        for page in doc:
            shift_names = get_shift_info_from_page(page)
            if not shift_names: continue
            
            drawings = page.get_drawings()
            ppm = (110.0 - 81.8) / 60.0
            origin_x = 81.8 - 4 * 60 * ppm
            
            words = page.get_text('words')
            sorted_shifts = sorted(shift_names.items(), key=lambda x: x[1])
            
            for idx, (shift_name, sy) in enumerate(sorted_shifts):
                
                loc_words = []
                time_texts_with_x = []
                for w in words:
                    if sy - 15 < w[1] < sy - 2:
                        loc_words.append((w[0], w[4]))
                    if sy < w[1] < sy + 25:
                        time_texts_with_x.append((w[0], w[4]))
                        
                loc_words.sort(key=lambda x: x[0])
                
                grouped_locs = []
                curr_text = ''
                curr_x = -100
                for x, t in loc_words:
                    if x - curr_x < 25:
                        curr_text += ' ' + t
                    else:
                        if curr_text: grouped_locs.append((curr_x, curr_text.strip()))
                        curr_text = t
                    curr_x = x
                if curr_text: grouped_locs.append((curr_x, curr_text.strip()))
                
                bars = []
                for d in drawings:
                    rect = d['rect']
                    if sy - 5 < rect.y0 < sy + 15 and rect.height > 2 and rect.width > 5:
                        fill = d.get('fill')
                        if fill and len(fill) == 3:
                            r, g, b = fill
                            if (r, g, b) != (1.0, 1.0, 1.0):
                                start_min = (rect.x0 - origin_x) / ppm
                                end_min = (rect.x1 - origin_x) / ppm
                                bars.append((rect.x0, rect.x1, round(start_min), round(end_min)))
                
                bars.sort(key=lambda x: x[0])
                if not bars: continue
                
                snapped_bars = []
                for bx0, bx1, s, e in bars:
                    s_snap = snap_time_advanced(s, time_texts_with_x, bx0, True)
                    e_snap = snap_time_advanced(e, time_texts_with_x, bx1, False)
                    snapped_bars.append((bx0, bx1, s_snap, e_snap))
                
                riprese = []
                sostas = []
                curr_start = snapped_bars[0][2]
                curr_end = snapped_bars[0][3]
                curr_end_x = snapped_bars[0][1]
                
                for b_x0, b_x1, s, e in snapped_bars[1:]:
                    if not riprese or s - curr_end > 30:
                        riprese.append([curr_start, curr_end])
                        
                        best_loc = ""
                        min_dist = 999
                        for lx, lt in grouped_locs:
                            dist = min(abs(lx - curr_end_x), abs(lx - b_x0))
                            if dist < min_dist and dist < 50:
                                min_dist = dist
                                best_loc = lt
                        
                        if best_loc:
                            bl = best_loc.lower()
                            if 'cas' in bl: best_loc = 'Caselle'
                            elif 'to' in bl or 'pn' in bl: best_loc = 'Torino'
                            elif 'pin' in bl: best_loc = 'Pinerolo'
                            
                        sostas.append(best_loc)
                        
                        curr_start = s
                        curr_end = e
                        curr_end_x = b_x1
                    else:
                        curr_end = max(curr_end, e)
                        curr_end_x = max(curr_end_x, b_x1)
                
                riprese.append([curr_start, curr_end])
                
                if riprese:
                    riprese[0][0] -= 10
                    riprese[-1][1] += 10
                    
                    sheet_name = pdf_name_to_sheet_name(shift_name)
                    if sheet_name and sheet_name not in all_shifts:
                        all_shifts[sheet_name] = {'riprese': riprese, 'sostas': sostas}
                        
    return all_shifts

shifts_2025 = extract_all_crew_2025()
print(f'Extracted {len(shifts_2025)} total matched shifts with ADVANCED OCR Snapping.')

def fmt_t(mins):
    mins = int(mins) % 1440
    return f"{mins//60:02d}.{mins%60:02d}"

cols_map = [
    (('F', 5), ('G', 6), ('H', 7)),
    (('I', 8), ('J', 9), ('K', 10)),
    (('L', 11), ('M', 12), ('N', 13)),
    (('O', 14), ('P', 15), ('Q', 16)),
    (('R', 17), ('S', 18), ('T', 19)),
    (('U', 20), ('V', 21), ('W', 22))
]

updates = []
matched = 0

for i, row in enumerate(data):
    if i == 0: continue
    
    name = row[0].strip()
    if not name or name in ['DISP','BIS','NOL','Turni']: continue
    
    if name in shifts_2025:
        # Clear first
        for (s_col, _), (e_col, _), (sosta_col, _) in cols_map:
            updates.append({'range': f'{s_col}{i+1}', 'values': [['']]})
            updates.append({'range': f'{e_col}{i+1}', 'values': [['']]})
            updates.append({'range': f'{sosta_col}{i+1}', 'values': [['']]})
            
        shift_info = shifts_2025[name]
        riprese = shift_info['riprese']
        sostas = shift_info['sostas']
        
        for r_idx, (s, e) in enumerate(riprese[:6]):
            s_col = cols_map[r_idx][0][0]
            e_col = cols_map[r_idx][1][0]
            updates.append({'range': f'{s_col}{i+1}', 'values': [[fmt_t(s)]]})
            updates.append({'range': f'{e_col}{i+1}', 'values': [[fmt_t(e)]]})
            
            if r_idx < len(riprese) - 1 and r_idx < len(sostas):
                sosta_col = cols_map[r_idx][2][0]
                updates.append({'range': f'{sosta_col}{i+1}', 'values': [[sostas[r_idx]]]})
        
        matched += 1

print(f"Preparing to update {matched} matched shifts in the Google Sheet...")
batch_size = 200
for i in range(0, len(updates), batch_size):
    ws.batch_update(updates[i:i+batch_size])
print("Update complete!")
