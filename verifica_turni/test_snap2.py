import fitz
import re

def extract_minutes(text):
    if re.match(r'^\d{2}$', text):
        return [int(text)]
    if re.match(r'^\d{4}$', text):
        return [int(text[:2]), int(text[2:])]
    return []

def snap_time_advanced(graphical_mins, texts_with_x, target_x, is_start):
    gm = graphical_mins % 60
    gh = graphical_mins // 60
    
    valid_mins = []
    # For start time, the text is usually slightly before target_x
    # For end time, the text is usually slightly before or exactly at target_x
    for x, t in texts_with_x:
        if abs(x - target_x) < 15:
            valid_mins.extend(extract_minutes(t))
            
    if not valid_mins:
        return graphical_mins
        
    # Convert all valid_mins to total minutes, resolving the hour
    candidate_times = []
    for m in valid_mins:
        diff = m - gm
        if diff > 30: diff -= 60
        elif diff < -30: diff += 60
        # If difference is too big, maybe it's not a minute (e.g. line number 3940)
        # But wait, 39, 40, 45 are all valid!
        candidate_times.append(graphical_mins + diff)
        
    # For start time, we want the EARLIEST time (minimum)
    # For end time, we want the LATEST time (maximum)
    if is_start:
        best_time = min(candidate_times)
    else:
        best_time = max(candidate_times)
        
    # Sanity check: don't deviate by more than 25 minutes from graphical
    if abs(best_time - graphical_mins) > 25:
        return graphical_mins
        
    return best_time

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
    snapped_s = snap_time_advanced(s, texts_with_x, x0, is_start=True)
    snapped_e = snap_time_advanced(e, texts_with_x, x1, is_start=False)
    print(f"Graphical: {s//60:02d}:{s%60:02d} - {e//60:02d}:{e%60:02d}  |  Snapped Advanced: {snapped_s//60:02d}:{snapped_s%60:02d} - {snapped_e//60:02d}:{snapped_e%60:02d}")
