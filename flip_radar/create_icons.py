import zlib
import struct

def make_png(width, height, output_path):
    # Generates a PNG with a blue gradient and stylized golden-yellow lightning/radar symbol
    raw_data = bytearray()
    
    for y in range(height):
        raw_data.append(0) # filter byte (None)
        for x in range(width):
            # Center coordinates
            cx = x - width / 2
            cy = y - height / 2
            dist = (cx*cx + cy*cy) ** 0.5
            radius = width * 0.44

            # Background: deep slate to dark blue (#0f172a to #1e3a8a)
            factor = y / height
            r = int(15 * (1 - factor) + 30 * factor)
            g = int(23 * (1 - factor) + 58 * factor)
            b = int(42 * (1 - factor) + 138 * factor)

            # Circular badge outline
            if abs(dist - radius) < width * 0.02:
                r, g, b = 59, 130, 246 # bright blue outline
            elif dist < radius:
                # Inside radar circle: slightly lighter
                r = int(r * 1.3)
                g = int(g * 1.3)
                b = int(b * 1.4)
                
                # Stylized Lightning / Flash shape in center
                # Simple lightning polygon test
                nx = cx / (width * 0.3)
                ny = cy / (height * 0.3)
                
                # Check if point is inside lightning
                is_bolt = False
                if -0.6 <= ny <= 0.6:
                    if ny < 0 and (-0.3 - ny*0.4 <= nx <= 0.3 - ny*0.2):
                        is_bolt = True
                    elif ny >= 0 and (-0.5 - ny*0.2 <= nx <= 0.1 - ny*0.4):
                        is_bolt = True
                
                if is_bolt:
                    # Gold / Amber color for bolt
                    r, g, b = 245, 158, 11
                elif abs(dist - radius * 0.5) < width * 0.01:
                    # Radar inner ring
                    r, g, b = 96, 165, 250

            raw_data.extend((min(255, r), min(255, g), min(255, b), 255))

    # Compress IDAT
    compressed = zlib.compress(bytes(raw_data))

    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = zlib.crc32(c) & 0xffffffff
        return struct.pack('>I', len(data)) + c + struct.pack('>I', crc)

    png = b'\x89PNG\r\n\x1a\n'
    # IHDR
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    png += chunk(b'IHDR', ihdr)
    # IDAT
    png += chunk(b'IDAT', compressed)
    # IEND
    png += chunk(b'IEND', b'')

    with open(output_path, 'wb') as f:
        f.write(png)
    print(f"Generated {output_path} ({width}x{height})")

make_png(192, 192, '/home/antonio/flip_radar/icon-192.png')
make_png(512, 512, '/home/antonio/flip_radar/icon-512.png')
