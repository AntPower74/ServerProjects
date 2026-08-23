import fitz

doc = fitz.open('Turni settembre 2026/Crew_Graph__LUSERNA.pdf')
page = doc[0]
drawings = page.get_drawings()

# Lu001 is at Y=49.9
for d in drawings:
    rect = d['rect']
    # Check if the drawing overlaps with the Y band of Lu001
    if 50 < rect.y0 < 75:
        # We only care about horizontal bars (height is small, width is large)
        if rect.height > 2 and rect.width > 5:
            # Convert X coordinates to times
            x_05 = 76.56
            pixels_per_min = 39.0 / 60.0
            
            start_mins = 5 * 60 + (rect.x0 - x_05) / pixels_per_min
            end_mins = 5 * 60 + (rect.x1 - x_05) / pixels_per_min
            
            s_h, s_m = int(start_mins // 60), int(start_mins % 60)
            e_h, e_m = int(end_mins // 60), int(end_mins % 60)
            
            print(f"Bar: {s_h:02d}:{s_m:02d} to {e_h:02d}:{e_m:02d} (Width: {rect.width:.1f}, Color: {d.get('fill')})")
