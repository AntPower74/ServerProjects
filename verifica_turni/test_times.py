import fitz
import re

def get_times_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    words = page.get_text('words')
    
    x_05 = 76.56
    pixels_per_min = 39.0 / 60.0
    
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
        
    for i in range(len(shifts)):
        s_y0 = shifts[i]['y0']
        if i + 1 < len(shifts):
            s_y1 = shifts[i+1]['y0']
        else:
            s_y1 = s_y0 + 25
            
        shift_name = shifts[i]['name']
        
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
                        
        time_points = sorted(list(set(time_points)))
        print(f"{shift_name}: {[f'{t//60:02d}:{t%60:02d}' for t in time_points]}")

get_times_from_pdf('Turni settembre 2026/Crew_Graph__LUSERNA.pdf')
