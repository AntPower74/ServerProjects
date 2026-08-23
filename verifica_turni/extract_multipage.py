import fitz
import re
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def pdf_name_to_sheet_name(pdf_name, valid_names):
    if pdf_name in valid_names:
        return pdf_name
    m = re.match(r'^([A-Z][a-z])(\d+)$', pdf_name)
    if m:
        prefix = m.group(1)
        num = int(m.group(2))
        candidate = f"{prefix}{num*10:04d}"
        if candidate in valid_names:
            return candidate
    return None

def get_shift_name(page):
    words = page.get_text('words')
    for w in words:
        if re.match(r'^[A-Z][a-z]\d{4}$', w[4]) and w[1] < 50:
            return w[4]
    for w in words:
        if re.match(r'^[A-Z][a-z]\d{3}$', w[4]) and w[1] < 100:
            return w[4]
    return None

def extract_all_optibus(pdf_path, valid_names):
    doc = fitz.open(pdf_path)
    n = len(doc)
    results = {}
    
    i = 0
    while i < n:
        page = doc[i]
        shift_name = get_shift_name(page)
        
        if not shift_name:
            i += 1
            continue
        
        # Collect text from this page and all continuation pages
        combined_text = page.get_text().replace('\n', ' ')
        
        # Check if this page continues on next page
        j = i + 1
        while j < n and 'pagina seguente' in doc[j-1].get_text().lower():
            combined_text += ' ' + doc[j].get_text().replace('\n', ' ')
            j += 1
        
        # Now extract from combined text
        m = re.search(r'SIGN ON:\s*(\d{2}:\d{2})[\s,]*SIGN OFF:\s*(\d{2}:\d{2})', combined_text)
        if not m:
            i = j
            continue
        
        sign_on  = m.group(1).replace(':', '.')
        sign_off = m.group(2).replace(':', '.')
        
        # Collect ALL PAUSAs from combined text (deduplicate)
        pauses_raw = re.findall(r'PAUSA\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})', combined_text)
        pauses = sorted(set(pauses_raw))
        
        riprese = []
        curr = sign_on
        for ps, pe in pauses:
            riprese.append((curr, ps.replace(':', '.')))
            curr = pe.replace(':', '.')
        riprese.append((curr, sign_off))
        
        sheet_name = pdf_name_to_sheet_name(shift_name, valid_names)
        if sheet_name:
            results[sheet_name] = riprese
        
        i = j  # Skip continuation pages
    
    return results

# Load sheet names
url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
ws = client.open_by_url(url).worksheet('Tabella Turni scol 2026')
valid_names = set(ws.col_values(1))

# Extract from main Cartellini PDF (all formats)
all_shifts = extract_all_optibus('Cartellini turni da settembre 2026.pdf', valid_names)
print(f"Extracted {len(all_shifts)} shifts from main Cartellini PDF")
print("Pe0170:", all_shifts.get('Pe0170'))
print("Pe0180:", all_shifts.get('Pe0180'))
print("Lu0010:", all_shifts.get('Lu0010'))
print("Lu0020:", all_shifts.get('Lu0020'))

with open('exact_shift_times.json', 'w') as f:
    json.dump(all_shifts, f, indent=2)

