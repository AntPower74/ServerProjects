import fitz

def test_parse(pdf_path, target_shift):
    doc = fitz.open(pdf_path)
    for page_num, page in enumerate(doc):
        text = page.get_text()
        if target_shift in text:
            print(f"--- Found {target_shift} on page {page_num} of {pdf_path} ---")
            blocks = page.get_text('blocks')
            
            # Filter out empty blocks
            blocks = [b for b in blocks if b[4].strip()]
            
            # Sort blocks by Y coordinate, then X coordinate
            blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
            
            for i, b in enumerate(blocks):
                x0, y0, x1, y1, t, block_no, block_type = b
                t_clean = t.replace('\n', ' | ')
                print(f"[{i:03d}] Y:{y0:6.1f} X:{x0:6.1f} -> {t_clean}")
            return True
    return False

test_parse('Cartellini turni da settembre 2026.pdf', 'Lu001')
