import pdfplumber
import re

PDF_PATH = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini lun-ven 2026.pdf"

targets = ['Ba3510', 'Bo3020', 'Ca6010', 'Ca0020', 'Pi0070']

with pdfplumber.open(PDF_PATH) as pdf:
    for page_idx, page in enumerate(pdf.pages):
        text = page.extract_text()
        for t in targets:
            if t in text:
                print(f"==================================================")
                print(f"📄 TROVATO {t} A PAGINA {page_idx + 1}")
                print(f"==================================================")
                lines = [l for l in text.split('\n') if any(w in l for w in [t, 'Inizio', 'Fine', 'Nastro', '280', '275', 'Disp', 'Sosta', 'Ponte Chisone', 'OSASCO', 'Bobbio'])]
                for l in lines[:15]:
                    print("  ", l)
