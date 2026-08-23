#!/usr/bin/env python3
"""
dedup_offerte.py — Rimuove offerte duplicate da offerte.json
Criteri:
  1. Titolo esatto uguale
  2. Titolo normalizzato uguale (ignora spazi/punteggiatura/maiuscole)
  3. Stesso negozio + stesso prezzo + titoli con ≥80% di caratteri in comune
"""
import json, re, shutil, os, sys
from pathlib import Path

FILE_OFFERTE = "/home/antonio/sitoofferte/offerte.json"

def normalizza(titolo):
    return re.sub(r'[^a-z0-9]', '', titolo.lower())

def similarita(a, b):
    sa, sb = set(normalizza(a)), set(normalizza(b))
    if not sa or not sb:
        return 0
    return len(sa & sb) / max(len(sa), len(sb))

def dedup(offerte):
    viste = []
    for o in offerte:
        titolo = o.get("title", "")
        prezzo = o.get("newPrice", "")
        negozio = o.get("store", "")
        duplicato = False
        for v in viste:
            # Criterio 1: titolo esatto
            if v.get("title", "") == titolo:
                duplicato = True; break
            # Criterio 2: titolo normalizzato
            if normalizza(v.get("title", "")) == normalizza(titolo):
                duplicato = True; break
            # Criterio 3: stesso negozio + stesso prezzo + titoli simili
            if v.get("store","") == negozio and v.get("newPrice","") == prezzo:
                if similarita(v.get("title",""), titolo) >= 0.80:
                    duplicato = True; break
        if not duplicato:
            viste.append(o)
    return viste

def main():
    if not os.path.exists(FILE_OFFERTE):
        print(f"File {FILE_OFFERTE} non trovato.")
        return

    with open(FILE_OFFERTE, "r", encoding="utf-8") as f:
        offerte = json.load(f)

    prima = len(offerte)
    offerte_clean = dedup(offerte)
    dopo = len(offerte_clean)
    rimossi = prima - dopo

    print(f"Offerte prima: {prima} | dopo: {dopo} | rimossi: {rimossi}")

    with open(FILE_OFFERTE, "w", encoding="utf-8") as f:
        json.dump(offerte_clean, f, indent=4, ensure_ascii=False)

    print(f"✅ Aggiornato {FILE_OFFERTE}")

if __name__ == "__main__":
    main()
