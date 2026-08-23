import fitz
import re
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import timedelta

def parse_t(t_str):
    """Parse '04.20' to minutes"""
    if not t_str or not t_str.strip(): return None
    t_str = t_str.strip()
    if '.' not in t_str: return None
    try:
        h, m = t_str.split('.')
        return int(h)*60 + int(m)
    except: return None

def fmt_t(mins):
    if mins is None: return '--:--'
    mins = mins % (24*60)
    return f"{mins//60:02d}.{mins%60:02d}"

def add_min(mins, delta):
    return (mins + delta) % (24*60)

# ---- Extract times from Crew Graph PDFs ----
def extract_crew_graph(pdf_path):
    """Extract shift start/end/num_riprese from Crew Graph PDF using graphical bars"""
    doc = fitz.open(pdf_path)
    shifts = {}
    
    for page in doc:
        words = page.get_text('words')
        # Find hour labels in header row (Y ~ 30-50)
        hour_labels = [(w[0], int(w[4])) for w in words 
                       if w[4].isdigit() and len(w[4]) <= 2 
                       and 20 < w[1] < 55 and int(w[4]) < 24]
        if not hour_labels: continue
        hour_labels.sort()
        if len(hour_labels) < 2: continue
        
        # Calculate pixels per minute
        x0, h0 = hour_labels[0]
        x1, h1 = hour_labels[1]
        if h1 == h0: continue
        ppm = (x1 - x0) / 60.0  # pixels per minute
        origin_x = x0 - h0 * 60 * ppm  # X at time 00:00
        
        # Find shift names and their Y positions
        drawings = page.get_drawings()
        shift_names = {}
        for w in words:
            if re.match(r'^[A-Z][a-z]\d{3,4}$', w[4]) and w[1] > 55:
                shift_names[w[4]] = w[1]
        
        if not shift_names: continue
        
        # Sort shifts by Y
        sorted_shifts = sorted(shift_names.items(), key=lambda x: x[1])
        
        for idx, (shift_name, sy) in enumerate(sorted_shifts):
            next_y = sorted_shifts[idx+1][1] if idx+1 < len(sorted_shifts) else sy + 20
            
            # Find grey/colored bars for this shift
            bars = []
            for d in drawings:
                rect = d['rect']
                if sy - 2 < rect.y0 < next_y and rect.height > 2 and rect.width > 5:
                    fill = d.get('fill')
                    if fill and len(fill) == 3:
                        r, g, b = fill
                        # Grey bars (driving) or colored bars
                        if (0.4 < r < 0.95 and abs(r-g) < 0.15 and abs(g-b) < 0.15):
                            start_min = (rect.x0 - origin_x) / ppm
                            end_min = (rect.x1 - origin_x) / ppm
                            bars.append((round(start_min), round(end_min)))
            
            bars.sort()
            if not bars: continue
            
            # Merge bars with gap <= 30 min -> riprese
            riprese = []
            for s, e in bars:
                if not riprese or s - riprese[-1][1] > 30:
                    riprese.append([s, e])
                else:
                    riprese[-1][1] = max(riprese[-1][1], e)
            
            if riprese:
                total_start = riprese[0][0]
                total_end   = riprese[-1][1]
                shifts[shift_name] = {
                    'start': total_start,
                    'end':   total_end,
                    'num_riprese': len(riprese),
                    'riprese': riprese
                }
    
    return shifts

# Load all crew graph data
crew_data = {}
for pdf in ['Crew_Graph__LUSERNA.pdf','Crew_Graph__PEROSA.pdf','Crew_Graph__PINEROLO.pdf',
            'Crew_Graph__PIOBESI.pdf','Crew_Graph__PONT.pdf','Crew_Graph__TORINO.pdf']:
    d = extract_crew_graph(f'Turni settembre 2026/{pdf}')
    crew_data.update(d)

print(f"Crew Graph: {len(crew_data)} shifts found")

# Normalize crew names to sheet names (same *10 logic)
def crew_to_sheet_name(crew_name, valid_names):
    if crew_name in valid_names: return crew_name
    m = re.match(r'^([A-Z][a-z])(\d+)$', crew_name)
    if m:
        c = f"{m.group(1)}{int(m.group(2))*10:04d}"
        if c in valid_names: return c
    return None

# Load sheet data
url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
ws = client.open_by_url(url).worksheet('Tabella Turni scol 2026')
data = ws.get_all_values()
valid_names = set(r[0].strip() for r in data if r)

# Column indices (0-based): F=5,G=6,I=8,J=9,L=11,M=12,O=14,P=15,R=17,S=18,U=20,V=21
rip_start_cols = [5, 8, 11, 14, 17, 20]
rip_end_cols   = [6, 9, 12, 15, 18, 21]

skip = {'DISP','BIS','NOL','ACM','ACV','ADS','AF','AI','AM','APMAF','APMAT',
        'APNRO','APR','AREC','AS','AST','ASL','GL','RC','RF','FBS','RIP','','Turni'}

# Build sheet dict
sheet_shifts = {}
for row in data[1:]:
    name = row[0].strip()
    if name in skip or not name: continue
    starts = [parse_t(row[c]) for c in rip_start_cols if c < len(row) and row[c].strip()]
    ends   = [parse_t(row[c]) for c in rip_end_cols   if c < len(row) and row[c].strip()]
    starts = [x for x in starts if x is not None]
    ends   = [x for x in ends   if x is not None]
    if starts and ends:
        sheet_shifts[name] = {
            'first_start': starts[0],
            'last_end':    ends[-1],
            'num_riprese': len(starts)
        }

# Compare
TOLERANCE = 15  # minutes tolerance for graphical approximation
report = []

for crew_name, crew_info in sorted(crew_data.items()):
    sheet_name = crew_to_sheet_name(crew_name, valid_names)
    if not sheet_name: continue
    if sheet_name not in sheet_shifts: continue
    
    sheet_info = sheet_shifts[sheet_name]
    
    # Crew graph times + 10min (start) and -10min (end) to match cartellini
    crew_start_adj = add_min(crew_info['start'], 10)
    crew_end_adj   = add_min(crew_info['end'], -10)
    
    diff_start = abs(crew_start_adj - sheet_info['first_start'])
    if diff_start > 12*60: diff_start = 24*60 - diff_start  # wrap around midnight
    
    diff_end   = abs(crew_end_adj - sheet_info['last_end'])
    if diff_end > 12*60: diff_end = 24*60 - diff_end
    
    diff_rip = abs(crew_info['num_riprese'] - sheet_info['num_riprese'])
    
    issues = []
    if diff_start > TOLERANCE:
        issues.append(f"INIZIO: crew={fmt_t(crew_info['start'])}(+10={fmt_t(crew_start_adj)}) vs sheet={fmt_t(sheet_info['first_start'])} [diff={diff_start}min]")
    if diff_end > TOLERANCE:
        issues.append(f"FINE: crew={fmt_t(crew_info['end'])}(-10={fmt_t(crew_end_adj)}) vs sheet={fmt_t(sheet_info['last_end'])} [diff={diff_end}min]")
    if diff_rip > 0:
        issues.append(f"RIPRESE: crew={crew_info['num_riprese']} vs sheet={sheet_info['num_riprese']}")
    
    if issues:
        report.append((sheet_name, issues))

# Save report
with open('report_discrepanze.txt', 'w') as f:
    f.write(f"REPORT DISCREPANZE: Crew Graph vs Cartellini\n")
    f.write(f"Turni confrontati: {len(crew_data)}\n")
    f.write(f"Discrepanze trovate: {len(report)}\n\n")
    for name, issues in report:
        f.write(f"{'='*50}\n{name}:\n")
        for iss in issues:
            f.write(f"  !! {iss}\n")

print(f"\n{'='*60}")
print(f"Turni con dati in entrambe le fonti: {len([c for c in crew_data if crew_to_sheet_name(c, valid_names) in sheet_shifts])}")
print(f"Discrepanze trovate: {len(report)}")
print(f"{'='*60}\n")
for name, issues in report:
    print(f"{name}:")
    for iss in issues:
        print(f"  !! {iss}")

