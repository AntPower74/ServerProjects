#!/usr/bin/env python3
import fitz

doc = fitz.open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini lun-ven 2026.pdf")
page = doc[0] # Ba3510

print("=== RIGHE ESTRATTE DALLA PAGINA 1 (Ba3510) ===")
lines = page.get_text("text").split('\n')
for i, l in enumerate(lines):
    print(f"{i:3d}: {l}")
