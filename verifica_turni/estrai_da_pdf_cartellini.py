#!/usr/bin/env python3
"""
Estrattore e Parser Diretto dai Cartellini PDF Ufficiali
"""

import fitz # PyMuPDF
import json
import re
import os

pdf_path1 = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini lun-ven 2026.pdf"
pdf_path2 = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini_Azienda_Ufficiali_2026.pdf"

target_pdf = pdf_path1 if os.path.exists(pdf_path1) else pdf_path2

print(f"📄 Apertura PDF Cartellini: {target_pdf}")
doc = fitz.open(target_pdf)
print(f"📄 Totale Pagine Cartellini nel PDF: {len(doc)}")

# Mostriamo il testo della prima pagina per capire il layout
p0 = doc[0]
print("\n--- TESTO ESTRATTO DALLA PAGINA 1: ---")
print(p0.get_text())

