import fitz
import re
import json

def normalize_time(t):
    if '.' not in t: return t
    parts = t.split('.')
    return f"{int(parts[0]):02d}.{parts[1]}"

def extract_optibus_format(page):
    """Handles the 'Optibus' Cartellini format: SIGN ON, SIGN OFF, PAUSA"""
    words = page.get_text('words')
    shift_name = None
    for w in words:
        if re.match(r'^[A-Z][a-z]\d{3}$', w[4]) and w[1] < 100:
            shift_name = w[4]
            break
    if not shift_name: return None, None
    
    full_text = page.get_text().replace('\n', ' ')
    m = re.search(r'SIGN ON:\s*(\d{2}:\d{2})[\s,]*SIGN OFF:\s*(\d{2}:\d{2})', full_text)
    if not m: return shift_name, None
    
    sign_on = m.group(1).replace(':', '.')
    sign_off = m.group(2).replace(':', '.')
    pauses = re.findall(r'PAUSA\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})', full_text)
    pauses.sort()
    
    riprese = []
    curr = sign_on
    for ps, pe in pauses:
        riprese.append((curr, ps.replace(':', '.')))
        curr = pe.replace(':', '.')
    riprese.append((curr, sign_off))
    return shift_name, riprese

def extract_arriva_format(page):
    """Handles ARRIVA ITALIA Cartellino format: column-based I./F. Ripresa"""
    words = page.get_text('words')
    words.sort(key=lambda w: (w[1], w[0]))
    
    shift_name = None
    for w in words:
        if re.match(r'^[A-Z][a-z]\d{4}$', w[4]) and w[1] < 50:
            shift_name = w[4]
            break
    if not shift_name: return None, None
    
    lines = {}
    for w in words:
        y = round(w[1])
        found = False
        for k in lines:
            if abs(k-y) < 4:
                lines[k].append(w)
                found = True
                break
        if not found:
            lines[y] = [w]
    
    header_y = None
    i_rip_x = f_rip_x = None
    for y, row_words in sorted(lines.items()):
        row_text = ' '.join(w[4] for w in row_words)
        if 'I.' in row_text and 'Ripresa' in row_text and 'F.' in row_text:
            header_y = y
            hw = sorted(row_words, key=lambda w: w[0])
            for i_w, w in enumerate(hw):
                if w[4] == 'I.' and i_w+1 < len(hw) and hw[i_w+1][4] == 'Ripresa':
                    i_rip_x = w[0]
                if w[4] == 'F.' and i_w+1 < len(hw) and hw[i_w+1][4] == 'Ripresa':
                    f_rip_x = w[0]
            break
    
    if header_y is None or i_rip_x is None or f_rip_x is None:
        return shift_name, None
    
    block_i = []
    block_f = []
    for y in sorted(lines.keys()):
        if y <= header_y: continue
        row_words = sorted(lines[y], key=lambda w: w[0])
        row_text = ' '.join(w[4] for w in row_words)
        if any(kw in row_text for kw in ['Totali', 'ORE LAVORO', 'NASTRO', 'STRAORDINARI']): break
        
        for w in row_words:
            if re.match(r'^\d{1,2}\.\d{2}$', w[4]):
                if abs(w[0] - i_rip_x) < 25:
                    block_i.append(normalize_time(w[4]))
                elif abs(w[0] - f_rip_x) < 25:
                    block_f.append(normalize_time(w[4]))
    
    all_times = sorted([(t, 'I') for t in block_i] + [(t, 'F') for t in block_f])
    riprese = []
    curr_start = None
    for t, typ in all_times:
        if typ == 'I':
            if curr_start is None:
                curr_start = t
        elif typ == 'F':
            if curr_start is not None:
                riprese.append((curr_start, t))
                curr_start = None
    
    return shift_name, riprese if riprese else None

# Step 1: Optibus format (Lu, Pe, Pi partial) - most accurate source
optibus_shifts = {}
doc = fitz.open('Cartellini turni da settembre 2026.pdf')
for page in doc:
    name, riprese = extract_optibus_format(page)
    if name and riprese:
        m = re.match(r'^([A-Z][a-z])(\d+)$', name)
        if m:
            norm = f"{m.group(1)}{int(m.group(2)):03d}0"
            optibus_shifts[norm] = riprese

print(f"Optibus format: {len(optibus_shifts)} shifts")
print(f"  Lu0010: {optibus_shifts.get('Lu0010')}")
print(f"  Lu0020: {optibus_shifts.get('Lu0020')}")

# Step 2: ARRIVA format - only add shifts NOT already in optibus_shifts
arriva_shifts = {}
for pdf in ['cartellini scolastici torino attuali.pdf', 'cartellini scolastici pinerolo attuali.pdf']:
    doc = fitz.open(pdf)
    for page in doc:
        name, riprese = extract_arriva_format(page)
        if name and riprese and name not in optibus_shifts:
            arriva_shifts[name] = riprese

print(f"ARRIVA format (new only): {len(arriva_shifts)} shifts")
for k in ['Pi0040', 'To0260', 'To0600', 'Pt0040']:
    print(f"  {k}: {arriva_shifts.get(k)}")

all_shifts = {**arriva_shifts, **optibus_shifts}
print(f"\nTotal combined: {len(all_shifts)} shifts")

with open('exact_shift_times.json', 'w') as f:
    json.dump(all_shifts, f, indent=2)

