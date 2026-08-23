import fitz
import re
import json

def add_min(t_str, minutes):
    """Add minutes to a time string like '04.30' and return '04.20'"""
    h, m = int(t_str[:2]), int(t_str[3:])
    total = h * 60 + m + minutes
    if total < 0: total += 24*60
    return f"{total//60:02d}.{total%60:02d}"

def extract_optibus_format(page):
    """Handles Luserna/Pinerolo/Perosa style: SIGN ON, SIGN OFF, PAUSA"""
    full_text = page.get_text().replace('\n', ' ')
    
    words = page.get_text('words')
    shift_name = None
    for w in words:
        if re.match(r'^[A-Z][a-z]\d{3}$', w[4]) and w[1] < 100:
            shift_name = w[4]
            break
    if not shift_name: return None, None
    
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
    """Handles ARRIVA ITALIA (Torino/Pinerolo) style: tabella corse with I.Ripresa / F.Ripresa columns"""
    words = page.get_text('words')
    words.sort(key=lambda w: (w[1], w[0]))
    
    full_text = page.get_text().replace('\n', ' ')
    
    # Find shift name like To0260, Pi0010, Pt0040 etc.
    shift_name = None
    for w in words:
        if re.match(r'^[A-Z][a-z]\d{4}$', w[4]) and w[1] < 50:
            shift_name = w[4]
            break
    if not shift_name: return None, None
    
    # Group words by Y
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
    
    # find header row (contains 'I.' and 'Ripresa' and 'F.')
    header_y = None
    for y, row_words in sorted(lines.items()):
        row_text = ' '.join(w[4] for w in row_words)
        if 'I.' in row_text and 'Ripresa' in row_text and 'F.' in row_text:
            header_y = y
            break
    
    if header_y is None: return shift_name, None
    
    header_words = sorted(lines[header_y], key=lambda w: w[0])
    
    # Find X positions of "I. Ripresa" and "F. Ripresa"
    i_rip_x = None
    f_rip_x = None
    for i_w, w in enumerate(header_words):
        if w[4] == 'I.' and i_w+1 < len(header_words) and header_words[i_w+1][4] == 'Ripresa':
            i_rip_x = w[0]
        if w[4] == 'F.' and i_w+1 < len(header_words) and header_words[i_w+1][4] == 'Ripresa':
            f_rip_x = w[0]
    
    if i_rip_x is None or f_rip_x is None: return shift_name, None
    
    # Walk data rows
    time_pairs = []
    for y in sorted(lines.keys()):
        if y <= header_y: continue
        row_words = sorted(lines[y], key=lambda w: w[0])
        row_text = ' '.join(w[4] for w in row_words)
        
        # Skip totals/summary lines
        if any(kw in row_text for kw in ['Totali', 'ORE LAVORO', 'NASTRO', 'STRAORDINARI', 'AGENTE', 'MAGG.']):
            break
        
        # Find time at I.Ripresa column and F.Ripresa column (within 20px X tolerance)
        i_time = None
        f_time = None
        for w in row_words:
            if re.match(r'^\d{1,2}\.\d{2}$', w[4]):
                if abs(w[0] - i_rip_x) < 20:
                    i_time = w[4]
                elif abs(w[0] - f_rip_x) < 20:
                    f_time = w[4]
        
        if i_time and f_time:
            # Normalize to 2-digit hour
            if '.' in i_time and len(i_time) <= 4:
                i_time = i_time.zfill(5)
            if '.' in f_time and len(f_time) <= 4:
                f_time = f_time.zfill(5)
            time_pairs.append((i_time, f_time))
    
    if not time_pairs: return shift_name, None
    
    # Now group pairs into riprese (merge consecutive where gap <= 30 min)
    riprese = []
    for i_t, f_t in time_pairs:
        if not riprese:
            riprese.append([i_t, f_t])
        else:
            last_f = riprese[-1][1]
            # Parse both
            lf_h, lf_m = int(last_f[:2]), int(last_f[3:])
            it_h, it_m = int(i_t[:2]), int(i_t[3:])
            gap = (it_h*60 + it_m) - (lf_h*60 + lf_m)
            if gap < 0: gap += 24*60
            if gap <= 30:
                riprese[-1][1] = f_t  # extend current ripresa
            else:
                riprese.append([i_t, f_t])
    
    return shift_name, [(r[0], r[1]) for r in riprese]

# Process all PDFs
all_shifts = {}

# 1. Optibus format (Luserna, Perosa, Pinerolo regional)
doc = fitz.open('Cartellini turni da settembre 2026.pdf')
for page in doc:
    name, riprese = extract_optibus_format(page)
    if name and riprese:
        # Normalize: Lu001 -> Lu0010
        m = re.match(r'^([A-Z][a-z])(\d+)$', name)
        if m:
            norm = f"{m.group(1)}{int(m.group(2)):03d}0"
            all_shifts[norm] = riprese

# 2. ARRIVA format (Torino and Pinerolo extra)
for pdf in ['cartellini scolastici torino attuali.pdf', 'cartellini scolastici pinerolo attuali.pdf']:
    doc = fitz.open(pdf)
    for page in doc:
        name, riprese = extract_arriva_format(page)
        if name and riprese:
            all_shifts[name] = riprese

print(f"Total shifts parsed: {len(all_shifts)}")
for k in ['Lu0010', 'Lu0020', 'Pe0080', 'Pi0040', 'To0260', 'Pt0040', 'To0600']:
    print(f"  {k}: {all_shifts.get(k)}")

with open('exact_shift_times.json', 'w') as f:
    json.dump(all_shifts, f, indent=2)

