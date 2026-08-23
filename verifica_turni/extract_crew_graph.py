import re
import fitz


TURNO_RE = re.compile(r'^[A-Za-z][A-Za-z0-9]{2,9}$')
PAID_RE = re.compile(r'^\((\d{1,2}):(\d{2})\)$')
HOUR_TICK_Y = 34.4  # empirically constant across files/pages (header row)


def fit_hour_scale(words):
    ticks = [w for w in words if len(w[4]) == 2 and w[4].isdigit() and abs(w[1] - HOUR_TICK_Y) < 1]
    if len(ticks) < 3:
        return None
    ticks.sort(key=lambda w: w[0])
    hours = []
    prev = None
    for w in ticks:
        h = int(w[4])
        if prev is not None and h < prev - 12:  # midnight wrap
            h += 24 * ((prev - h) // 24 + 1)
        hours.append(h)
        prev = h
    xs = [(w[0] + w[2]) / 2 for w in ticks]
    n = len(xs)
    mean_x = sum(xs) / n
    mean_h = sum(hours) / n
    num = sum((x - mean_x) * (h - mean_h) for x, h in zip(xs, hours))
    den = sum((x - mean_x) ** 2 for x in xs)
    a = num / den  # hours per px
    b = mean_h - a * mean_x
    return a, b  # hour = a*x + b


def x_to_time(x, scale):
    a, b = scale
    hour = a * x + b
    hour = hour % 24
    hh = int(hour)
    mm = round((hour - hh) * 60)
    if mm == 60:
        mm = 0
        hh = (hh + 1) % 24
    return f"{hh:02d}:{mm:02d}"


def find_riprese(intervals, scale, min_minutes=31, touch_tol=1.5):
    if not intervals:
        return []
    ivs = sorted(intervals, key=lambda p: p[0])
    merged = [list(ivs[0])]
    for x0, x1 in ivs[1:]:
        if x0 <= merged[-1][1] + touch_tol:
            merged[-1][1] = max(merged[-1][1], x1)
        else:
            merged.append([x0, x1])

    riprese = []
    for (prev_x0, prev_x1), (next_x0, next_x1) in zip(merged, merged[1:]):
        a, _ = scale
        gap_minutes = round((next_x0 - prev_x1) * a * 60)
        if gap_minutes >= min_minutes:
            t0 = x_to_time(prev_x1, scale)
            t1 = x_to_time(next_x0, scale)
            riprese.append(f"{t0}-{t1} ({gap_minutes}min)")
    return riprese


def extract_page_shifts(page):
    words = page.get_text('words')
    scale = fit_hour_scale(words)
    if scale is None:
        return []

    # pair turno-code words with the "(H:MM)" word directly below them
    labels = []
    turno_words = [w for w in words if TURNO_RE.match(w[4])]
    paid_words = [w for w in words if PAID_RE.match(w[4])]
    for tw in turno_words:
        tx0, ty0, tx1, ty1 = tw[:4]
        best = None
        best_dy = 999
        for pw in paid_words:
            px0, py0 = pw[0], pw[1]
            if abs(px0 - tx0) < 15 and 0 < (py0 - ty1) < 15:
                dy = py0 - ty1
                if dy < best_dy:
                    best_dy = dy
                    best = pw
        if best:
            labels.append({'turno': tw[4], 'paid': best[4].strip('()'), 'y0': ty0})

    labels.sort(key=lambda l: l['y0'])

    drawings = page.get_drawings()
    page_w = page.rect.width
    shapes = []
    bar_shapes = []  # primary colored/filled trip segments only (for gap/riprese detection)
    for d in drawings:
        r = d['rect']
        w = r.x1 - r.x0
        h = r.y1 - r.y0
        if w > 700 or h > 200:
            continue  # full-width/height separators, not bars
        if w < 0.5 and h > 15:
            continue  # tall vertical hour gridlines (dotted hour separators)
        if r.x0 < 50:
            continue  # left-margin labels/gridline origin
        shapes.append(r)
        if d.get('fill') is not None and 4.5 <= h <= 6.0:
            bar_shapes.append(r)

    if len(labels) > 1:
        spacing = (labels[-1]['y0'] - labels[0]['y0']) / (len(labels) - 1)
    else:
        spacing = 30

    results = []
    for i, lab in enumerate(labels):
        band_top = lab['y0'] - spacing * 0.2
        band_bot = lab['y0'] + spacing * 0.77
        xs0 = [s.x0 for s in shapes if band_top <= s.y0 <= band_bot or band_top <= s.y1 <= band_bot]
        xs1 = [s.x1 for s in shapes if band_top <= s.y0 <= band_bot or band_top <= s.y1 <= band_bot]
        if not xs0:
            continue
        start_x = min(xs0)
        end_x = max(xs1)

        bar_intervals = [(s.x0, s.x1) for s in bar_shapes if band_top <= s.y0 <= band_bot or band_top <= s.y1 <= band_bot]
        riprese = find_riprese(bar_intervals, scale)

        results.append({
            'turno': lab['turno'],
            'paid_graph': lab['paid'],
            'inizio_grafico': x_to_time(start_x, scale),
            'fine_grafico': x_to_time(end_x, scale),
            'riprese': '; '.join(riprese),
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
