#!/usr/bin/env python3
"""Importa il tab "CalendarioSCOL" (calendario scolastico parametrico 2017-2050)
nella tabella school_calendar_years - copia fedele, un anno per riga, cosi'
il pannello puo' poi mostrarla/modificarla invece di dover ricalcolare tutto
a mano ogni anno.

Run: /home/antonio/verifica_turni/venv/bin/python3 migration/05_import_school_calendar.py
"""
import os
import sqlite3

import gspread
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = '/home/antonio/verifica_turni/credentials.json'
SPREADSHEET_ID = '19JoM03xFRXKKTENZuP5mjkbxTPHnYtmUWvXkzYJhZhg'
SHEET_GID = 1247775424
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'turni.db')

MESI = {
    'gennaio': 1, 'febbraio': 2, 'marzo': 3, 'aprile': 4, 'maggio': 5, 'giugno': 6,
    'luglio': 7, 'agosto': 8, 'settembre': 9, 'ottobre': 10, 'novembre': 11, 'dicembre': 12,
}


def parse_easter(s):
    """'16 aprile 2017' -> '2017-04-16'"""
    parts = s.strip().split()
    if len(parts) != 3:
        return None
    day, month_name, year = parts
    month = MESI.get(month_name.lower())
    if not month:
        return None
    return f'{int(year):04d}-{month:02d}-{int(day):02d}'


def to_int(v):
    v = (v or '').strip()
    return int(v) if v.isdigit() else None


def to_bool(v):
    return 1 if (v or '').strip().upper() == 'TRUE' else 0


def main():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    ws = client.open_by_key(SPREADSHEET_ID).get_worksheet_by_id(SHEET_GID)
    rows = ws.get('A3:Q36')  # riga 1-2 = intestazioni, dati da riga 3 (anno 2017) in poi

    conn = sqlite3.connect(DB_PATH)
    imported = 0
    for row in rows:
        row = row + [''] * (17 - len(row))  # pad fino a colonna Q
        year_s = row[0].strip()
        if not year_s.isdigit():
            continue
        year = int(year_s)
        easter = parse_easter(row[2])
        conn.execute(
            '''INSERT INTO school_calendar_years (
                 year, easter_date, summer_end_day_june, summer_start_day_september,
                 agosto_start_day, agosto_end_day,
                 carnevale1_day, carnevale1_month, carnevale2_day, carnevale2_month,
                 epifania_active, liberazione_active, lavoro_active,
                 forze_armate_active, tutti_santi_active, immacolata_active
               ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(year) DO UPDATE SET
                 easter_date=excluded.easter_date,
                 summer_end_day_june=excluded.summer_end_day_june,
                 summer_start_day_september=excluded.summer_start_day_september,
                 agosto_start_day=excluded.agosto_start_day,
                 agosto_end_day=excluded.agosto_end_day,
                 carnevale1_day=excluded.carnevale1_day, carnevale1_month=excluded.carnevale1_month,
                 carnevale2_day=excluded.carnevale2_day, carnevale2_month=excluded.carnevale2_month,
                 epifania_active=excluded.epifania_active, liberazione_active=excluded.liberazione_active,
                 lavoro_active=excluded.lavoro_active, forze_armate_active=excluded.forze_armate_active,
                 tutti_santi_active=excluded.tutti_santi_active, immacolata_active=excluded.immacolata_active
            ''',
            (
                year, easter, to_int(row[3]), to_int(row[4]), to_int(row[5]), to_int(row[6]),
                to_int(row[7]), to_int(row[8]), to_int(row[9]), to_int(row[10]),
                to_bool(row[11]), to_bool(row[12]), to_bool(row[13]),
                to_bool(row[14]), to_bool(row[15]), to_bool(row[16]),
            ),
        )
        imported += 1
    conn.commit()
    print(f'imported {imported} years')


if __name__ == '__main__':
    main()
