import fitz
import re
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load valid sheet names to validate our mappings
url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
ws = client.open_by_url(url).worksheet('Tabella Turni scol 2026')
valid_sheet_names = set(ws.col_values(1))

def pdf_name_to_sheet_name(pdf_name, valid_names):
    """Smart mapping: try direct match first, then *10 rule"""
    # Direct match (same name in sheet)
    if pdf_name in valid_names:
        return pdf_name
    
    # Try multiply by 10 (for Pe0014 -> Pe0140 etc.)
    m = re.match(r'^([A-Z][a-z])(\d+)$', pdf_name)
    if m:
        prefix = m.group(1)
        num = int(m.group(2))
        candidate = f"{prefix}{num*10:04d}"
        if candidate in valid_names:
            return candidate
    
    return None  # No match found

def extract_optibus_page(page):
    words = page.get_text('words')
    shift_name = None
    
    for w in words:
        if re.match(r'^[A-Z][a-z]\d{4}$', w[4]) and w[1] < 50:
            shift_name = w[4]; break
    if not shift_name:
        for w in words:
            if re.match(r'^[A-Z][a-z]\d{3}$', w[4]) and w[1] < 100:
                shift_name = w[4]; break
    if not shift_name: return None, None
    
    full_text = page.get_text().replace('\n', ' ')
    m = re.search(r'SIGN ON:\s*(\d{2}:\d{2})[\s,]*SIGN OFF:\s*(\d{2}:\d{2})', full_text)
    if not m: return shift_name, None
    
    sign_on  = m.group(1).replace(':', '.')
    sign_off = m.group(2).replace(':', '.')
    pauses   = re.findall(r'PAUSA\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})', full_text)
    pauses.sort()
    
    riprese = []
    curr = sign_on
    for ps, pe in pauses:
        riprese.append((curr, ps.replace(':', '.')))
        curr = pe.replace(':', '.')
    riprese.append((curr, sign_off))
    return shift_name, riprese

# Start fresh from the correct base (Optibus 3-digit already correct)
all_shifts = {}

doc = fitz.open('Cartellini turni da settembre 2026.pdf')
matched = 0
unmatched = []
for page in doc:
    pdf_name, riprese = extract_optibus_page(page)
    if not pdf_name or not riprese: continue
    
    sheet_name = pdf_name_to_sheet_name(pdf_name, valid_sheet_names)
    if sheet_name:
        all_shifts[sheet_name] = riprese
        matched += 1
    else:
        unmatched.append(pdf_name)

print(f"Matched: {matched}, Unmatched: {unmatched}")

# Also add ARRIVA format from other PDFs (for shifts not already found)
def extract_arriva_format(page):
    words = page.get_text('words')
    words.sort(key=lambda w: (w[1], w[0]))
    shift_name = None
    for w in words:
        if re.match(r'^[A-Z][a-z]\d{4}$', w[4]) and w[1] < 50:
            shift_name = w[4]; break
    if not shift_name: return None, None
    
    lines = {}
    for w in words:
        y = round(w[1])
        found = False
        for k in lines:
            if abs(k-y) < 4: lines[k].append(w); found=True; break
        if not found: lines[y] = [w]
    
    header_y = i_rip_x = f_rip_x = None
    for y, rw in sorted(lines.items()):
        rt = ' '.join(w[4] for w in rw)
        if 'I.' in rt and 'Ripresa' in rt and 'F.' in rt:
            header_y = y
            hw = sorted(rw, key=lambda w: w[0])
            for i_w, w in enumerate(hw):
                if w[4] == 'I.' and i_w+1 < len(hw) and hw[i_w+1][4] == 'Ripresa': i_rip_x = w[0]
                if w[4] == 'F.' and i_w+1 < len(hw) and hw[i_w+1][4] == 'Ripresa': f_rip_x = w[0]
            break
    if not header_y or not i_rip_x or not f_rip_x: return shift_name, None
    
    block_i = []; block_f = []
    for y in sorted(lines.keys()):
        if y <= header_y: continue
        rw = sorted(lines[y], key=lambda w: w[0])
        rt = ' '.join(w[4] for w in rw)
        if any(kw in rt for kw in ['Totali','ORE LAVORO','NASTRO','STRAORDINARI']): break
        for w in rw:
            if re.match(r'^\d{1,2}\.\d{2}$', w[4]):
                t = f"{int(w[4].split('.')[0]):02d}.{w[4].split('.')[1]}"
                if abs(w[0]-i_rip_x) < 25: block_i.append(t)
                elif abs(w[0]-f_rip_x) < 25: block_f.append(t)
    
    all_t = sorted([(t,'I') for t in block_i]+[(t,'F') for t in block_f])
    riprese = []; curr_start = None
    for t, typ in all_t:
        if typ == 'I' and curr_start is None: curr_start = t
        elif typ == 'F' and curr_start is not None:
            riprese.append((curr_start, t)); curr_start = None
    return shift_name, riprese if riprese else None

for pdf in ['cartellini scolastici torino attuali.pdf', 'cartellini scolastici pinerolo attuali.pdf']:
    doc = fitz.open(pdf)
    for page in doc:
        name, riprese = extract_arriva_format(page)
        if name and riprese:
            sheet_name = pdf_name_to_sheet_name(name, valid_sheet_names)
            if sheet_name and sheet_name not in all_shifts:
                all_shifts[sheet_name] = riprese

print(f"Total: {len(all_shifts)} shifts")
for k in ['Pe0140', 'Pt0010', 'Pt0040', 'To0260', 'To0320']:
    print(f"  {k}: {all_shifts.get(k)}")

with open('exact_shift_times.json', 'w') as f:
    json.dump(all_shifts, f, indent=2)

