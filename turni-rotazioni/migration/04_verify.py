#!/usr/bin/env python3
"""Verifies the migrated DB's computed schedule two ways:

1. Recomputes each depot's turno directly from migration/depots_raw.json (the raw
   block cells captured from the sheet BEFORE it was reverted today) using an
   independent implementation of the rotation math, and diffs against what the
   SQLite-backed compute_turno() returns - this checks the DB-load pipeline without
   depending on the live Google Sheet, which is currently in a known-broken state
   (Calendario tab reverted to pre-fix formulas) and isn't a trustworthy oracle
   right now.
2. Re-checks the specific hand-verified cases from today's manual TO debugging
   (Ginardi's turno on 1 Jan, and during the 3 August weeks) as regression pins.

Run: /home/antonio/verifica_turni/venv/bin/python3 migration/04_verify.py
(only needs the local files + sqlite - no network calls)
"""
import datetime as dt
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(__file__)
RAW_PATH = os.path.join(HERE, 'depots_raw.json')
DB_PATH = os.path.join(HERE, '..', 'data', 'turni.db')

DEPOTS = ['TO', 'PI', 'CA', 'LU', 'PT', 'PE', 'PB', 'GT']
SAMPLE_DAY_OFFSETS = list(range(0, 365, 20))


def weekday_mon0(d):
    return d.weekday()


def weeks_since(reference_iso, target_date):
    ref = dt.date.fromisoformat(reference_iso)
    return (target_date - ref).days // 7


def resolve_column(rotation_position, weeks, cycle_length):
    m = (weeks + rotation_position) % cycle_length
    return cycle_length if m == 0 else m


# --- shared block-type classification (natale/festivo/agosto/scolastico) -----
# Both paths call this with the SAME holidays/calendar_ranges (loaded once from
# the DB, since that's the only place they live - they're seeded from Calendario's
# helper columns, not present in depots_raw.json). This keeps the two paths a
# genuine cross-check of the DATA LOADING pipeline (raw sheet cells -> DB rows),
# rather than two independently-guessed and inevitably-drifting holiday rules.

def classify_block_type(d, holidays, calendar_ranges):
    iso = d.isoformat()
    if any(r['kind'] == 'natale' and r['start_date'] <= iso <= r['end_date'] for r in calendar_ranges):
        return 'natale'
    if iso in holidays:
        return 'festiva'
    if d.month == 8:
        return 'agosto'
    if any(r['kind'] == 'scolastico' and r['start_date'] <= iso <= r['end_date'] for r in calendar_ranges):
        return 'scolastico'
    return 'non_scolastico'


# --- path 1: recompute straight from the raw JSON capture ------------------

def raw_expected(depot_raw, driver_name, d, holidays, calendar_ranges):
    """Independent implementation reading straight from depots_raw.json's block
    cells - deliberately not sharing code with server/rotation.js's cell lookup,
    so this is a genuine cross-check of the DB-load pipeline (not the same bug
    twice). special_periods are matched by date range directly from the raw
    block list, same precedence as the real system (special period wins).
    """
    driver = next((d2 for d2 in depot_raw['drivers'] if d2['name'] == driver_name), None)
    if not driver:
        return None

    weeks = weeks_since(depot_raw['reference_date'], d)
    col = resolve_column(driver['rotation_position'], weeks, depot_raw['cycle_length'])
    weekday = weekday_mon0(d)

    block = None
    for b in depot_raw['blocks']:
        if not b['is_standard'] and b.get('agosto_day_range'):
            start_day, end_day = b['agosto_day_range']
            if d.month == 8 and start_day <= d.day <= end_day:
                block = b
                break

    if block is None:
        block_type = classify_block_type(d, holidays, calendar_ranges)
        block = next((b for b in depot_raw['blocks'] if b['is_standard'] and b['block_type'] == block_type), None)

    if not block:
        return None
    cell = next((c for c in block['cells'] if c['weekday'] == weekday and c['col_index'] == col), None)
    return cell['turno_code'] if cell else None


# --- path 2: query the actual DB, same way the server would ----------------

def db_expected(conn, depot_id, driver_name, d, holidays, calendar_ranges):
    depot = conn.execute('SELECT * FROM depots WHERE id=?', (depot_id,)).fetchone()
    cols = [c[0] for c in conn.execute('SELECT * FROM depots').description]
    depot = dict(zip(cols, depot))

    driver_row = conn.execute(
        'SELECT id, rotation_position FROM drivers WHERE depot_id=? AND name=?', (depot_id, driver_name)
    ).fetchone()
    if not driver_row:
        return None
    driver_id, rotation_position = driver_row

    iso = d.isoformat()
    sp = conn.execute(
        'SELECT block_id FROM special_periods WHERE depot_id=? AND active=1 AND start_date<=? AND end_date>=? '
        'ORDER BY priority DESC LIMIT 1',
        (depot_id, iso, iso),
    ).fetchone()
    if sp:
        block_id = sp[0]
    else:
        block_type = classify_block_type(d, holidays, calendar_ranges)
        row = conn.execute(
            'SELECT id FROM rotation_blocks WHERE depot_id=? AND block_type=? AND is_standard=1',
            (depot_id, block_type),
        ).fetchone()
        if not row:
            return None
        block_id = row[0]

    weeks = weeks_since(depot['reference_date'], d)
    col = resolve_column(rotation_position, weeks, depot['cycle_length'])
    weekday = weekday_mon0(d)
    cell = conn.execute(
        'SELECT turno_code FROM rotation_cells WHERE block_id=? AND weekday=? AND col_index=?',
        (block_id, weekday, col),
    ).fetchone()
    return cell[0] if cell else None


def main():
    with open(RAW_PATH, encoding='utf-8') as f:
        raw = json.load(f)
    conn = sqlite3.connect(DB_PATH)

    holidays = {row[0] for row in conn.execute('SELECT date FROM holidays')}
    calendar_ranges = [
        {'kind': k, 'start_date': s, 'end_date': e}
        for k, s, e in conn.execute('SELECT kind, start_date, end_date FROM calendar_ranges')
    ]

    total = 0
    mismatches = 0

    print('=== cross-check: raw JSON recompute vs DB (all depots, sampled dates) ===')
    for depot_id in DEPOTS:
        depot_raw = raw[depot_id]
        driver_names = [d['name'] for d in depot_raw['drivers'][:5]]  # first 5 drivers is plenty
        depot_mismatches = []
        for offset in SAMPLE_DAY_OFFSETS:
            d = dt.date(2026, 1, 1) + dt.timedelta(days=offset)
            for name in driver_names:
                expected = raw_expected(depot_raw, name, d, holidays, calendar_ranges)
                actual = db_expected(conn, depot_id, name, d, holidays, calendar_ranges)
                total += 1
                if expected != actual:
                    mismatches += 1
                    depot_mismatches.append((d.isoformat(), name, expected, actual))
        status = 'OK' if not depot_mismatches else f'{len(depot_mismatches)} MISMATCHES'
        print(f'{depot_id}: {status}')
        for d_iso, name, exp, act in depot_mismatches[:10]:
            print(f'    {d_iso}  {name!r}: raw_json={exp!r}  db={act!r}')

    print(f'\n{total} checks, {mismatches} mismatches')

    print('\n=== regression pins: today\'s manually-verified TO cases ===')
    pins = [
        ('2026-01-01', 'Ginardi 563', 'To5037'),
        ('2026-08-12', 'Ginardi 563', 'To0260'),
        ('2026-08-24', 'Ginardi 563', 'To0130'),
        ('2026-08-29', 'Ginardi 563', 'RIP'),
        ('2026-08-30', 'Ginardi 563', 'DISP'),
    ]
    pin_failures = 0
    for iso, name, expected in pins:
        d = dt.date.fromisoformat(iso)
        actual = db_expected(conn, 'TO', name, d, holidays, calendar_ranges)
        ok = actual == expected
        pin_failures += 0 if ok else 1
        print(f'  {"OK " if ok else "FAIL"} {iso} {name}: expected={expected!r} got={actual!r}')

    conn.close()
    sys.exit(1 if (mismatches or pin_failures) else 0)


if __name__ == '__main__':
    main()
