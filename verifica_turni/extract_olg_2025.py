import re
import fitz
from collections import defaultdict

from extract_crew_graph_2025 import TURNO_RE, IGNORE

NUM_RE = re.compile(r'^-?\d+,\d+$')


def get_turno_rows(page):
    words = page.get_text('words')
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
        rows.append((dep_words[0][1], turno))
    rows.sort(key=lambda r: r[0])
    return [t for _, t in rows]


def get_olg_column(page):
    words = page.get_text('words')
    headers = {w[4]: w[0] for w in words if w[4] in ('OLG', 'Nastro', 'Rip')}
    if 'OLG' not in headers:
        return []
    olg_x = headers['OLG']
    nums = [w for w in words if NUM_RE.match(w[4]) and abs(w[0] - olg_x) < 10]
    nums.sort(key=lambda w: w[1])
    result = []
    for w in nums:
        h, m = w[4].split(',')
        result.append(f"{int(h)}:{m}")
    return result


def extract_olg_by_turno(pdf_path):
    doc = fitz.open(pdf_path)
    result = {}
    for page in doc:
        turni = get_turno_rows(page)
        olg_vals = get_olg_column(page)
        if len(turni) != len(olg_vals):
            print(f"ATTENZIONE pagina con mismatch: {len(turni)} turni vs {len(olg_vals)} valori OLG")
        for turno, olg in zip(turni, olg_vals):
            result[turno.upper()] = olg
    return result


if __name__ == '__main__':
    d = extract_olg_by_turno('turni scolastici 2025 grafici/Turni dal 100925_giov.base scolastico.pdf')
    print(f"Totale: {len(d)}")
    for k, v in list(d.items())[:15]:
        print(k, v)
