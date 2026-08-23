import fitz

doc = fitz.open('Turni settembre 2026/Crew_Graph__LUSERNA.pdf')
page = doc[0]
words = page.get_text('words')

# Find the hours row. It should be near Y=34
hour_xs = {}
for w in words:
    x0, y0, x1, y1, text, block_no, line_no, word_no = w
    if 30 < y0 < 40 and text.isdigit():
        hour_xs[int(text)] = x0
        print(f"Hour {text} at X={x0:.2f}")
        
# Now let's find the words for Lu001 (Y roughly between 49 and 75)
print("\nLu001 Words:")
for w in words:
    x0, y0, x1, y1, text, block_no, line_no, word_no = w
    if 49 < y0 < 75:
        print(f"Y={y0:.1f}, X={x0:.1f} -> {text}")
