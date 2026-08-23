import pdfplumber

PDF_PATH = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini lun-ven 2026.pdf"

with pdfplumber.open(PDF_PATH) as pdf:
    for page_idx, page in enumerate(pdf.pages):
        text = page.extract_text()
        if 'To0660' in text:
            print(f"📄 To0660 si trova a PAGINA {page_idx + 1} del PDF ufficiale:")
            for l in text.split('\n'):
                if any(w in l for w in ['To0660', 'MOPAR', '275', '282', '277', '121', 'Nastro', 'Inizio']):
                    print("  ", l)
