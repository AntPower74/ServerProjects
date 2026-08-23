import fitz
import re

def extract_break_locations(pdf_path, target_shift, break_times):
    doc = fitz.open(pdf_path)
    for page in doc:
        text = page.get_text()
        if target_shift in text:
            words = page.get_text('words')
            locations = {}
            for target_time in break_times:
                time_words = [w for w in words if target_time in w[4]]
                if not time_words:
                    continue
                
                # Pick the time word that is part of a table (X is roughly 216, 372, or 531)
                # Sometimes times appear in other places
                for tw in time_words:
                    y_time = tw[1]
                    x_time = tw[0]
                    
                    # Words on same line and to the left within ~160 pixels
                    loc_words = [w for w in words if abs(w[1] - y_time) < 5 and (x_time - 160) < w[0] < x_time]
                    loc_words.sort(key=lambda w: w[0])
                    
                    clean_loc = []
                    for lw in loc_words:
                        if re.match(r'^\d{2}:\d{2}$', lw[4]): continue
                        if 'ID' in lw[4] or 'corsa' in lw[4] or 'Linea' in lw[4] or '|' in lw[4]: continue
                        if re.match(r'^\d+$', lw[4]): continue
                        if lw[4] == '-': continue
                        clean_loc.append(lw[4])
                        
                    loc_str = " ".join(clean_loc).strip()
                    loc_str = re.sub(r'\.{3,}', '', loc_str).strip()
                    if loc_str and loc_str != "PAUSA":
                        locations[target_time] = loc_str
                        break
            return locations
    return {}

print(extract_break_locations('Cartellini turni da settembre 2026.pdf', 'Lu001', ['06:29', '09:20']))
print(extract_break_locations('Cartellini turni da settembre 2026.pdf', 'Lu006', ['17:33', '19:30']))
