import fitz
import re
import json

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
            shift_names[name] = y
            
    return shift_names

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
            words = page.get_text('words')
            hour_labels = [(w[0], int(w[4])) for w in words 
                           if w[4].isdigit() and len(w[4]) <= 2 
                           and 40 < w[1] < 75 and int(w[4]) < 24]
            if not hour_labels: continue
            hour_labels.sort()
            if len(hour_labels) < 2: continue
            
            x0, h0 = hour_labels[0]
            x1, h1 = hour_labels[1]
            if h1 == h0: continue
            ppm = (x1 - x0) / 60.0  
            origin_x = x0 - h0 * 60 * ppm  
            
            shift_names = get_shift_names_from_page(page)
            if not shift_names: continue
            
            drawings = page.get_drawings()
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
                            # Exclude white which is background
                            if (r, g, b) != (1.0, 1.0, 1.0):
                                start_min = (rect.x0 - origin_x) / ppm
                                end_min = (rect.x1 - origin_x) / ppm
                                bars.append((round(start_min), round(end_min)))
                
                bars.sort()
                if not bars: continue
                
                riprese = []
                for s, e in bars:
                    # Stacco > 30 min = nuova ripresa
                    if not riprese or s - riprese[-1][1] > 30:
                        riprese.append([s, e])
                    else:
                        riprese[-1][1] = max(riprese[-1][1], e)
                
                if riprese:
                    # Normalize shift names like 01FT010S to FT010S and 01To0090 to To0090
                    # The leading digits are sometimes there
                    clean_name = re.sub(r'^\d+', '', shift_name)
                    # We only care about the best riprese for each shift name.
                    # It's possible the same shift appears multiple times (e.g. across PDFs)
                    if clean_name not in all_shifts:
                        all_shifts[clean_name] = riprese
                        
    return all_shifts

shifts_2025 = extract_all_crew_2025()
print(f'Extracted {len(shifts_2025)} total unique shifts from 2025 PDFs.')

with open('shifts_2025.json', 'w') as f:
    json.dump(shifts_2025, f, indent=2)

print('Sample shifts:')
for k, v in list(shifts_2025.items())[:5]:
    fmt_v = [(f"{(s%1440)//60:02d}.{s%60:02d}", f"{(e%1440)//60:02d}.{e%60:02d}") for s, e in v]
    print(f"  {k}: {fmt_v}")
