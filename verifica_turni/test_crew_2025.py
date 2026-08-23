import fitz
import re

def get_shift_names_from_page(page):
    words = page.get_text('words')
    # Filter words that could be part of a shift name in the left column (X roughly 25 to 70)
    # The shift name parts are typically at X > 30 and X < 70, with Y > 50
    # Let's group words by Y coordinate
    lines = {}
    for w in words:
        if 20 < w[0] < 80 and w[1] > 50:
            y = round(w[1], 1)
            found = False
            for k in lines:
                if abs(k - y) < 2:
                    lines[k].append(w)
                    found = True
                    break
            if not found:
                lines[y] = [w]
    
    shift_names = {}
    for y, line_words in lines.items():
        line_words.sort(key=lambda x: x[0])
        # Join the words
        name = "".join(w[4] for w in line_words)
        # Clean up if needed
        # It should look like To0090, FT010S, etc.
        if re.match(r'^[A-Z]{1,2}\d{1,4}[A-Z]?$', name) or re.match(r'^[A-Z][a-z]\d{1,4}[A-Z]?$', name):
            shift_names[name] = y
            
    return shift_names

def extract_crew_graph_2025(pdf_path):
    doc = fitz.open(pdf_path)
    shifts = {}
    
    for page in doc:
        words = page.get_text('words')
        hour_labels = [(w[0], int(w[4])) for w in words 
                       if w[4].isdigit() and len(w[4]) <= 2 
                       and 20 < w[1] < 55 and int(w[4]) < 24]
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
                        # Grey bars (driving) or colored bars
                        if (0.4 < r < 0.95 and abs(r-g) < 0.15 and abs(g-b) < 0.15):
                            start_min = (rect.x0 - origin_x) / ppm
                            end_min = (rect.x1 - origin_x) / ppm
                            bars.append((round(start_min), round(end_min)))
            
            bars.sort()
            if not bars: continue
            
            riprese = []
            for s, e in bars:
                # User constraint: gap > 30 minutes means new ripresa (da 31 in poi)
                if not riprese or s - riprese[-1][1] > 30:
                    riprese.append([s, e])
                else:
                    riprese[-1][1] = max(riprese[-1][1], e)
            
            if riprese:
                shifts[shift_name] = riprese
                
    return shifts

pdf = 'Turni settembre 2025/Turni dal 100925_giov.base scolastico.pdf'
shifts = extract_crew_graph_2025(pdf)
print(f'Found {len(shifts)} shifts.')
for k, v in list(shifts.items())[:10]:
    # Format minutes to HH.MM
    fmt_v = [(f"{(s%1440)//60:02d}.{s%60:02d}", f"{(e%1440)//60:02d}.{e%60:02d}") for s, e in v]
    print(k, fmt_v)
