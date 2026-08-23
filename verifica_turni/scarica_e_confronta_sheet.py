#!/usr/bin/env python3
"""
Download del Google Sheet e confronto 1-to-1 con i dati estratti dai PDF dei cartellini
"""

import urllib.request
import csv
import json
import os

SHEET_ID = "1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM"
GID = "347790035"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
CSV_PATH = "/home/antonio/verifica_turni/corse_google_sheet.csv"

print(f"📥 Download del Google Sheet da: {CSV_URL}")
try:
    req = urllib.request.Request(CSV_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
        with open(CSV_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
    print(f"✅ Google Sheet scaricato con successo in: {CSV_PATH}")
except Exception as e:
    print(f"❌ Errore nel download del Google Sheet: {e}")

