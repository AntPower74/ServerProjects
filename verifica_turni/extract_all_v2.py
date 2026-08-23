import fitz
import re
import json

def normalize_time(t):
    """Normalize '4.40' to '04.40'"""
    if '.' not in t: return t
    parts = t.split('.')
    return f"{int(parts[0]):02d}.{parts[1]}"

def add_min(t_str, minutes):
    h, m = int(t_str[:2]), int(t_str[3:])
    total = h * 60 + m + minutes
    if total < 0: total += 24*60
    return f"{total//60:02d}.{total%60:02d}"

def extract_optibus_format(page):
    """Handles Luserna/Pinerolo/Perosa style: SIGN ON, SIGN OFF, PAUSA"""
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
    """Handles ARRIVA ITALIA (Torino/Pinerolo) style"""
    words = page.get_text('words')
    words.sort(key=lambda w: (w[1], w[0]))
    
    shift_name = None
    for w in words:
        if re.match(r'^[A-Z][a-z]\d{4}$', w[4]) and w[1] < 50:
            shift_name = w[4]
            break
    if not shift_name: return None, None
    
    # Group by Y
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
    
    # Find header row
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
    
    # Collect all I.Ripresa and F.Ripresa times from each data row
    all_i_times = []
    all_f_times = []
    
    for y in sorted(lines.keys()):
        if y <= header_y: continue
        row_words = sorted(lines[y], key=lambda w: w[0])
        row_text = ' '.join(w[4] for w in row_words)
        if any(kw in row_text for kw in ['Totali', 'ORE LAVORO', 'NASTRO', 'STRAORDINARI']): break
        
        for w in row_words:
            if re.match(r'^\d{1,2}\.\d{2}$', w[4]):
                if abs(w[0] - i_rip_x) < 25:
                    all_i_times.append((y, normalize_time(w[4])))
                elif abs(w[0] - f_rip_x) < 25:
                    all_f_times.append((y, normalize_time(w[4])))
    
    if not all_i_times: return shift_name, None
    
    # Build riprese: pair i_times with f_times
    # First I.Ripresa is start of first ripresa
    # Last F.Ripresa is end of last ripresa
    # Middle: each F.Ripresa followed by next I.Ripresa is a break
    
    all_i_times.sort()
    all_f_times.sort()
    
    i_vals = [t for _, t in all_i_times]
    f_vals = [t for _, t in all_f_times]
    
    # Start = first I, end = last F
    # Build by pairing: ripresa 1 = i[0] to f[0], etc.
    # But some rows only have I or only have F (Trasf rows)
    
    # Better approach: find the distinct "I.Ripresa" values (not many per shift)
    # Each real ripresa has EXACTLY ONE I.Ripresa row (first row of that block)
    # Each real ripresa has EXACTLY ONE F.Ripresa row (last row of that block)
    
    # Group consecutive rows
    riprese = []
    rip_start = i_vals[0] if i_vals else None
    rip_end = f_vals[-1] if f_vals else None
    
    # Find break points: a F.Ripresa followed by an I.Ripresa with big gap
    # Use Y-based pairing: each ripresa block has its own I and F
    
    # Group data rows by ripresa block: I.Ripresa marks start, F.Ripresa marks end
    block_i = []
    block_f = []
    
    for y in sorted(lines.keys()):
        if y <= header_y: continue
        row_words = sorted(lines[y], key=lambda w: w[0])
        row_text = ' '.join(w[4] for w in row_words)
        if any(kw in row_text for kw in ['Totali', 'ORE LAVORO', 'NASTRO']): break
        
        has_i = any(abs(w[0] - i_rip_x) < 25 and re.match(r'^\d{1,2}\.\d{2}$', w[4]) for w in row_words)
        has_f = any(abs(w[0] - f_rip_x) < 25 and re.match(r'^\d{1,2}\.\d{2}$', w[4]) for w in row_words)
        
        if has_i:
            t = normalize_time(next(w[4] for w in row_words if abs(w[0]-i_rip_x)<25 and re.match(r'^\d{1,2}\.\d{2}$', w[4])))
            block_i.append(t)
        if has_f:
            t = normalize_time(next(w[4] for w in row_words if abs(w[0]-f_rip_x)<25 and re.match(r'^\d{1,2}\.\d{2}$', w[4])))
            block_f.append(t)
    
    # Merge into riprese: each I followed by the NEXT F (chronologically in between)
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

# Process all PDFs
all_shifts = {}

# 1. Optibus format
doc = fitz.open('Cartellini turni da settembre 2026.pdf')
for page in doc:
    name, riprese = extract_optibus_format(page)
    if name and riprese:
        m = re.match(r'^([A-Z][a-z])(\d+)$', name)
        if m:
            norm = f"{m.group(1)}{int(m.group(2)):03d}0"
            all_shifts[norm] = riprese

# 2. ARRIVA format
for pdf in ['cartellini scolastici torino attuali.pdf', 'cartellini scolastici pinerolo attuali.pdf']:
    doc = fitz.open(pdf)
    for page in doc:
        name, riprese = extract_arriva_format(page)
        if name and riprese:
            all_shifts[name] = riprese

print(f"Total shifts parsed: {len(all_shifts)}")
for k in ['Lu0010', 'Lu0020', 'Pe0080', 'Pi0040', 'To0260', 'To0600', 'Pt0040']:
    r = all_shifts.get(k)
    print(f"  {k}: {r}")

with open('exact_shift_times.json', 'w') as f:
    json.dump(all_shifts, f, indent=2)

