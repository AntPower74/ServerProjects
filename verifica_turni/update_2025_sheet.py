import fitz
import re
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_shift_names_from_page(page):
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
            # Clean leading digits (e.g. 01To0090 -> To0090)
            clean_name = re.sub(r'^\d+', '', name)
            # Map Pe0014 -> Pe0140 rule
            m = re.match(r'^([A-Z][a-z])(\d+)$', clean_name)
            if m:
                clean_name = f"{m.group(1)}{int(m.group(2))*10:04d}"
            shift_names[clean_name] = y
            
    return shift_names

def extract_all_crew_2025():
    # Only using weekday school shifts for the main table
    pdfs = ['Turni settembre 2025/Turni dal 100925_giov.base scolastico.pdf']
    all_shifts = {}
    
    for pdf_path in pdfs:
        doc = fitz.open(pdf_path)
        for page in doc:
            shift_names = get_shift_names_from_page(page)
            if not shift_names: continue
            
            drawings = page.get_drawings()
            
            # Exact calibration for 2025 PDFs
            ppm = (110.0 - 81.8) / 60.0
            origin_x = 81.8 - 4 * 60 * ppm
            
            sorted_shifts = sorted(shift_names.items(), key=lambda x: x[1])
            
            for idx, (shift_name, sy) in enumerate(sorted_shifts):
                next_y = sorted_shifts[idx+1][1] if idx+1 < len(sorted_shifts) else sy + 30
                bars = []
                for d in drawings:
                    rect = d['rect']
                    if sy - 5 < rect.y0 < next_y and rect.height > 2 and rect.width > 5:
                        fill = d.get('fill')
                        if fill and len(fill) == 3:
                            r, g, b = fill
                            if (r, g, b) != (1.0, 1.0, 1.0):
                                start_min = (rect.x0 - origin_x) / ppm
                                end_min = (rect.x1 - origin_x) / ppm
                                bars.append((round(start_min), round(end_min)))
                
                bars.sort()
                if not bars: continue
                
                riprese = []
                for s, e in bars:
                    # Gap > 30 min means new ripresa
                    if not riprese or s - riprese[-1][1] > 30:
                        riprese.append([s, e])
                    else:
                        riprese[-1][1] = max(riprese[-1][1], e)
                
                # Apply 10 minutes accessory time
                # First ripresa starts 10 min early, last ripresa ends 10 min late
                if riprese:
                    riprese[0][0] -= 10
                    riprese[-1][1] += 10
                    
                    if shift_name not in all_shifts:
                        all_shifts[shift_name] = riprese
                        
    return all_shifts

shifts_2025 = extract_all_crew_2025()
print(f'Extracted {len(shifts_2025)} total unique shifts from weekday 2025 PDF.')

def fmt_t(mins):
    mins = int(mins) % 1440
    return f"{mins//60:02d}.{mins%60:02d}"

# Update Google Sheet
url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
ws = client.open_by_key('1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM').worksheet('Tabella Turni scol 2025')
data = ws.get_all_values()

# Column letters to index mapping
cols_map = [
    ('F', 5), ('G', 6),   # 1° Ripresa
    ('I', 8), ('J', 9),   # 2° Ripresa
    ('L', 11), ('M', 12), # 3° Ripresa
    ('O', 14), ('P', 15), # 4° Ripresa
    ('R', 17), ('S', 18), # 5° Ripresa
    ('U', 20), ('V', 21)  # 6° Ripresa
]

updates = []
matched = 0

for i, row in enumerate(data):
    if i == 0: continue
    name = row[0].strip()
    if not name or name in ['DISP','BIS','NOL','Turni']: continue
    
    if name in shifts_2025:
        riprese = shifts_2025[name]
        
        # Clear existing times in the 6 riprese slots
        for col_letter, col_idx in cols_map:
            updates.append({'range': f'{col_letter}{i+1}', 'values': [['']]})
            
        # Write new riprese
        for r_idx, (s, e) in enumerate(riprese[:6]):
            s_col = cols_map[r_idx*2][0]
            e_col = cols_map[r_idx*2 + 1][0]
            updates.append({'range': f'{s_col}{i+1}', 'values': [[fmt_t(s)]]})
            updates.append({'range': f'{e_col}{i+1}', 'values': [[fmt_t(e)]]})
            
        matched += 1

print(f"Preparing to update {matched} matched shifts in the Google Sheet...")
# Apply updates in batches
batch_size = 200
for i in range(0, len(updates), batch_size):
    ws.batch_update(updates[i:i+batch_size])
print("Update complete!")
