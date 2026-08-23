#!/usr/bin/env python3
import pdfplumber

pdf_path = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini lun-ven 2026.pdf"

with pdfplumber.open(pdf_path) as pdf:
    # Test on page 1 (Ba3510) and page for Ca0030
    for page_idx in [0, 8]:
        page = pdf.pages[page_idx]
        text = page.extract_text()
        print(f"=== PAGE {page_idx + 1} ===")
        print(text)
        print("\n" + "="*50 + "\n")
