import fitz
import re
import json

def extract_optibus_page(page):
    """Returns (pdf_name, riprese) from an Optibus-format page"""
    words = page.get_text('words')
    shift_name = None
    
    # Try 4-digit first (higher Y tolerance)
    for w in words:
        if re.match(r'^[A-Z][a-z]\d{4}$', w[4]) and w[1] < 50:
            shift_name = w[4]
            break
    if not shift_name:
        for w in words:
            if re.match(r'^[A-Z][a-z]\d{3}$', w[4]) and w[1] < 100:
                shift_name = w[4]
                break
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

def pdf_name_to_sheet_name(pdf_name):
    """Converts PDF shift name to Google Sheet name"""
    m3 = re.match(r'^([A-Z][a-z])(\d{3})$', pdf_name)
    if m3:
        # Pe001 -> Pe0010
        return f"{m3.group(1)}{int(m3.group(2)):03d}0"
    
    m4 = re.match(r'^([A-Z][a-z])(\d{4})$', pdf_name)
    if m4:
        # Pe0014 -> Pe0140 (multiply by 10)
        return f"{m4.group(1)}{int(m4.group(2))*10:04d}"
    
    return pdf_name

# Load existing shifts
try:
    with open('exact_shift_times.json') as f:
        all_shifts = json.load(f)
    print(f"Loaded {len(all_shifts)} existing shifts")
except:
    all_shifts = {}
    print("Starting fresh")

# Process main Cartellini PDF (has ALL formats)
doc = fitz.open('Cartellini turni da settembre 2026.pdf')
new_found = 0
for page in doc:
    pdf_name, riprese = extract_optibus_page(page)
    if not pdf_name or not riprese: continue
    
    sheet_name = pdf_name_to_sheet_name(pdf_name)
    if sheet_name not in all_shifts:
        all_shifts[sheet_name] = riprese
        new_found += 1
        print(f"  NEW: {pdf_name} -> {sheet_name}: {riprese}")

print(f"\nFound {new_found} new shifts. Total: {len(all_shifts)}")

with open('exact_shift_times.json', 'w') as f:
    json.dump(all_shifts, f, indent=2)

