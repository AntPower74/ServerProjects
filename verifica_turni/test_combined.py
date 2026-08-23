import fitz
import re

def get_riprese(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    x_05 = 76.56
    pixels_per_min = 39.0 / 60.0
    
    words = page.get_text('words')
    
    blocks = page.get_text('blocks')
    blocks = sorted(blocks, key=lambda b: b[1])
    
    shifts = []
    current_shift = None
    for b in blocks:
        x0, y0, x1, y1, text, block_no, block_type = b
        text = text.strip()
        if x0 < 30 and not text.startswith('(') and len(text) >= 2 and 'Crew Graph' not in text and 'Service:' not in text:
            if current_shift:
                shifts.append(current_shift)
            current_shift = {'name': text, 'y0': y0, 'y1': y1}
            continue
        if current_shift:
            current_shift['y1'] = y1
    if current_shift:
        shifts.append(current_shift)
        
    drawings = page.get_drawings()
    
    for i in range(len(shifts)):
        s_y0 = shifts[i]['y0']
        s_y1 = shifts[i+1]['y0'] if i + 1 < len(shifts) else s_y0 + 25
        shift_name = shifts[i]['name']
        
        # Get grey bars
        grey_bars = []
        for d in drawings:
            rect = d['rect']
            if s_y0 < rect.y0 < s_y1 and rect.height > 2 and rect.width > 20:
                # Grey colors usually have r == g == b
                color = d.get('fill')
                if color and len(color) == 3 and abs(color[0]-color[1]) < 0.01 and abs(color[1]-color[2]) < 0.01:
                    start_mins = 5 * 60 + (rect.x0 - x_05) / pixels_per_min
                    end_mins = 5 * 60 + (rect.x1 - x_05) / pixels_per_min
                    grey_bars.append((start_mins, end_mins))
                    
        grey_bars.sort()
        
        # Get time points from text
        time_points = []
        for w in words:
            w_x0, w_y0, w_x1, w_y1, w_text, _, _, _ = w
            if s_y0 - 2 <= w_y0 <= s_y1 - 2:
                clean_t = re.sub(r'(.)\1{2}', r'\1', w_text)
                if re.match(r'^\d{2}$', clean_t):
                    label_min = int(clean_t)
                    predicted_mins = 5 * 60 + (w_x0 - x_05) / pixels_per_min
                    
                    best_h = -1
                    min_diff = 9999
                    for h in range(0, 28):
                        diff = abs((h * 60 + label_min) - predicted_mins)
                        if diff < min_diff:
                            min_diff = diff
                            best_h = h
                    if min_diff < 30:
                        time_points.append(best_h * 60 + label_min)
                        
        # Also check for explicit HH:MM blocks
        for b in blocks:
            x0, y0, x1, y1, text, block_no, block_type = b
            if s_y0 <= y0 <= s_y1:
                clean_t = re.sub(r'(.)\1{2}', r'\1', text)
                for line in clean_t.split('\n'):
                    m = re.search(r'(\d{2}):(\d{2})', line)
                    if m:
                        time_points.append(int(m.group(1))*60 + int(m.group(2)))
        
        time_points = sorted(list(set(time_points)))
        
        riprese = []
        for bar_s, bar_e in grey_bars:
            # find points inside this bar (allow 15 mins slop)
            points_in_bar = [t for t in time_points if bar_s - 10 <= t <= bar_e + 10]
            if points_in_bar:
                r_s = min(points_in_bar)
                r_e = max(points_in_bar)
            else:
                r_s = bar_s - 7
                r_e = bar_e - 7
            riprese.append((r_s, r_e))
            
        print(f"{shift_name}: {[(f'{int(s//60):02d}.{int(s%60):02d}', f'{int(e//60):02d}.{int(e%60):02d}') for s, e in riprese]}")

get_riprese('Turni settembre 2026/Crew_Graph__LUSERNA.pdf')
