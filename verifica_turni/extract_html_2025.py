import re
import glob
from bs4 import BeautifulSoup

DIR = 'Turni settembre 2025 lun-ven'
GAP_MIN = 31


def to_min(hhmm):
    h, m = map(int, hhmm.split(':'))
    return h * 60 + m


def fmt_hm(total_min):
    h = (total_min // 60) % 24
    m = total_min % 60
    return f"{h:02d}:{m:02d}"


def nastro_str(inizio, fine):
    start = to_min(inizio)
    end = to_min(fine)
    if end < start:
        end += 24 * 60
    diff = end - start
    return f"{diff // 60:02d}:{diff % 60:02d}"


def count_riprese(legs):
    # legs: list of (ora_part, stop_part, ora_arr, stop_arr)
    intervals = []
    for ora_part, stop_part, ora_arr, stop_arr in legs:
        try:
            s = to_min(ora_part)
            e = to_min(ora_arr)
        except ValueError:
            continue
        if e < s:
            e += 24 * 60
        intervals.append((s, e, stop_part.strip().lower() == stop_arr.strip().lower()))

    if not intervals:
        return None

    intervals.sort(key=lambda t: t[0])
    gaps = 0
    prev_end = intervals[0][1]
    if intervals[0][2] and intervals[0][1] - intervals[0][0] >= GAP_MIN:
        gaps += 1
    for s, e, is_sosta in intervals[1:]:
        gap = s - prev_end
        if gap >= GAP_MIN:
            gaps += 1
        elif is_sosta and (e - s) >= GAP_MIN:
            gaps += 1
        prev_end = max(prev_end, e)
    return gaps + 1


def parse_file(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    tables = soup.find_all('table')
    if len(tables) < 2:
        return None

    header_rows = tables[0].find_all('tr')
    if len(header_rows) < 2:
        return None
    cells = [c.get_text(strip=True) for c in header_rows[1].find_all(['td', 'th'])]
    # ['', 'Cod. Turno', 'Descrizione', 'Ora Partenza', 'Ora Arrivo', 'Inizio validità', 'Fine validità']
    if len(cells) < 5:
        return None
    turno, descrizione, ora_partenza, ora_arrivo = cells[1], cells[2], cells[3], cells[4]
    if turno == '00000' or not ora_partenza or not ora_arrivo:
        return None

    legs = []
    for row in tables[1].find_all('tr')[1:]:
        c = [td.get_text(strip=True) for td in row.find_all('td')]
        if len(c) < 5:
            continue
        # Cod.Turno, Ora part., Partenza, Ora arrivo, Arrivo, Km, ...
        legs.append((c[1], c[2], c[3], c[4]))

    riprese = count_riprese(legs)

    return {
        'turno': turno,
        'descrizione': descrizione,
        'inizio': ora_partenza,
        'fine': ora_arrivo,
        'nastro': nastro_str(ora_partenza, ora_arrivo),
        'riprese': riprese,
    }


def prefix_of(turno):
    m = re.match(r'[A-Za-z]+', turno)
    return m.group(0) if m else turno


def extract_all():
    results = []
    for path in glob.glob(f'{DIR}/VisualizzaTurnoStandard*'):
        r = parse_file(path)
        if r:
            results.append(r)
    # dedupe by turno (keep first occurrence)
    seen = {}
    for r in results:
        if r['turno'] not in seen:
            seen[r['turno']] = r
    return list(seen.values())


if __name__ == '__main__':
    data = extract_all()
    print(f"Turni estratti: {len(data)}")
    for d in data[:10]:
        print(d)
