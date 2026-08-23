import fitz
import re

def snap_time(graphical_mins, texts_with_x, target_x):
    # graphical_mins is total minutes from midnight
    gm = graphical_mins % 60
    gh = graphical_mins // 60
    
    best_min = None
    min_dist_x = 999
    
    # texts_with_x is list of (x, text)
    valid_texts = []
    for x, t in texts_with_x:
        if abs(x - target_x) < 7 and re.match(r'^\d{2}$', t):
            valid_texts.append((x, int(t)))
            
    if not valid_texts:
        return graphical_mins
        
    # Pick the one closest to target_x
    valid_texts.sort(key=lambda item: abs(item[0] - target_x))
    best_text_min = valid_texts[0][1]
    
    # Construct the snapped time
    # if gh:gm = 20:50 and best = 45 -> 20:45
    # if gh:gm = 20:02 and best = 58 -> 19:58
    # if gh:gm = 19:58 and best = 02 -> 20:02
    
    # We find the smallest time difference
    diff = best_text_min - gm
    if diff > 30: diff -= 60
    elif diff < -30: diff += 60
    
    return graphical_mins + diff

doc = fitz.open('Turni settembre 2025/Turni dal 100925_giov.base scolastico.pdf')
page = doc[15]
words = page.get_text('words')

sy = 283.2
relevant_words = [w for w in words if sy < w[1] < sy + 25]
texts_with_x = [(w[0], w[4]) for w in relevant_words]

ppm = (110.0 - 81.8) / 60.0
origin_x = 81.8 - 4 * 60 * ppm
drawings = page.get_drawings()

bars = []
for d in drawings:
    rect = d['rect']
    if sy - 5 < rect.y0 < sy + 15 and rect.height > 2 and rect.width > 5:
        fill = d.get('fill')
        if fill and len(fill) == 3 and fill != (1.0, 1.0, 1.0):
            s = (rect.x0 - origin_x) / ppm
            e = (rect.x1 - origin_x) / ppm
            bars.append((rect.x0, rect.x1, round(s), round(e)))
bars.sort(key=lambda x: x[0])

for x0, x1, s, e in bars:
    snapped_s = snap_time(s, texts_with_x, x0)
    snapped_e = snap_time(e, texts_with_x, x1)
    print(f"Graphical: {s//60:02d}:{s%60:02d} - {e//60:02d}:{e%60:02d}  |  Snapped: {snapped_s//60:02d}:{snapped_s%60:02d} - {snapped_e//60:02d}:{snapped_e%60:02d}")
