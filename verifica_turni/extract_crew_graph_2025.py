import re
import fitz
from collections import defaultdict

from extract_crew_graph import x_to_time, find_riprese

BAR_HEIGHT = (9.5, 11.5)
TURNO_RE = re.compile(r'^[A-Za-z][A-Za-z0-9]{2,9}$')
IGNORE = {'turno', 'dep', 'dep.'}


def fit_hour_scale(words):
    from collections import Counter
    candidates = [w for w in words if len(w[4]) == 2 and w[4].isdigit()]
    by_y = defaultdict(list)
    for w in candidates:
        by_y[round(w[1], 1)].append(w)
    best_y, best_list = max(by_y.items(), key=lambda kv: len(kv[1]))
    if len(best_list) < 10:
        return None
    ticks = sorted(best_list, key=lambda w: w[0])
    hours = []
    prev = None
    for w in ticks:
        h = int(w[4])
        if prev is not None and h < prev - 12:
            h += 24 * ((prev - h) // 24 + 1)
        hours.append(h)
        prev = h
    xs = [(w[0] + w[2]) / 2 for w in ticks]
    n = len(xs)
    mean_x = sum(xs) / n
    mean_h = sum(hours) / n
    num = sum((x - mean_x) * (h - mean_h) for x, h in zip(xs, hours))
    den = sum((x - mean_x) ** 2 for x in xs)
    a = num / den
    b = mean_h - a * mean_x
    return a, b


def nastro_str(inizio, fine):
    if not inizio or not fine:
        return ''
    ih, im = map(int, inizio.split(':'))
    fh, fm = map(int, fine.split(':'))
    start = ih * 60 + im
    end = fh * 60 + fm
    if end < start:
        end += 24 * 60
    diff = end - start
    return f"{diff // 60:02d}:{diff % 60:02d}"


def extract_page_shifts(page):
    words = page.get_text('words')
    scale = fit_hour_scale(words)
    if scale is None:
        return []

    by_block = defaultdict(list)
    for w in words:
        by_block[w[5]].append(w)

    rows = []
    for block_id, ws in by_block.items():
        left = [w for w in ws if w[0] < 76]
        if not left:
            continue
        dep_words = [w for w in left if w[0] < 25]
        turno_words = [w for w in left if 25 <= w[0] < 76]
        if not dep_words or not turno_words:
            continue
        turno_words.sort(key=lambda w: w[0])
        turno = ''.join(w[4] for w in turno_words)
        if not TURNO_RE.match(turno) or turno.lower() in IGNORE:
            continue
        y0 = dep_words[0][1]
        rows.append({'turno': turno, 'y0': y0})

    rows.sort(key=lambda r: r['y0'])
    if len(rows) < 2:
        return []
    ys = [r['y0'] for r in rows]
    spacing = (ys[-1] - ys[0]) / (len(ys) - 1) if len(ys) > 1 else 39

    drawings = page.get_drawings()
    bar_shapes = []
    for d in drawings:
        r = d['rect']
        w = r.x1 - r.x0
        h = r.y1 - r.y0
        if w > 700 or h > 200:
            continue
        if r.x0 < 70:
            continue
        if d.get('fill') is not None and BAR_HEIGHT[0] <= h <= BAR_HEIGHT[1]:
            bar_shapes.append(r)

    results = []
    for row in rows:
        band_top = row['y0'] - spacing * 0.15
        band_bot = row['y0'] + spacing * 0.85
        in_band = [s for s in bar_shapes if band_top <= s.y0 <= band_bot or band_top <= s.y1 <= band_bot]
        if not in_band:
            continue
        start_x = min(s.x0 for s in in_band)
        end_x = max(s.x1 for s in in_band)
        intervals = [(s.x0, s.x1) for s in in_band]
        riprese = find_riprese(intervals, scale)
        inizio = x_to_time(start_x, scale)
        fine = x_to_time(end_x, scale)
        results.append({
            'turno': row['turno'],
            'inizio_grafico': inizio,
            'fine_grafico': fine,
            'nastro_grafico': nastro_str(inizio, fine),
            'n_riprese': len(riprese) + 1,
        })
    return results


def extract_file_shifts(pdf_path):
    doc = fitz.open(pdf_path)
    all_shifts = []
    for page in doc:
        all_shifts.extend(extract_page_shifts(page))
    return all_shifts


if __name__ == '__main__':
    import sys
    shifts = extract_file_shifts(sys.argv[1])
    for s in shifts:
        print(s)
    print(len(shifts))
