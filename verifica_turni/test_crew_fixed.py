import fitz
import re

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

doc = fitz.open('Turni settembre 2025/Turni dal 100925_giov.base scolastico.pdf')
page = doc[0]

# Fixed grid mapping
ppm = (110.0 - 81.8) / 60.0
origin_x = 81.8 - 4 * 60 * ppm

shift_names = get_shift_names_from_page(page)
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
                if (r, g, b) != (1.0, 1.0, 1.0):
                    start_min = (rect.x0 - origin_x) / ppm
                    end_min = (rect.x1 - origin_x) / ppm
                    bars.append((round(start_min), round(end_min)))
    
    bars.sort()
    riprese = []
    for s, e in bars:
        if not riprese or s - riprese[-1][1] > 30:
            riprese.append([s, e])
        else:
            riprese[-1][1] = max(riprese[-1][1], e)
    
    fmt_v = [(f"{(s%1440)//60:02d}.{s%60:02d}", f"{(e%1440)//60:02d}.{e%60:02d}") for s, e in riprese]
    print(f"{shift_name}: {fmt_v}")
