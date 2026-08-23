#!/usr/bin/env python3
"""Agganciamento alle strade reali (via OSRM demo pubblico, a lotti di 10 punti)
dei 5 tracciati della linea 268 Torino-Caselle, + snap delle fermate al tracciato
piu' vicino, + colori distinti per traccia (estensione Garmin, letta da OsmAnd)."""
import zipfile, csv, io, json, math, time, urllib.request, urllib.error
from xml.sax.saxutils import escape

SRC = '/home/antonio/Percorsi/google_transit_caselle_23052025 (1).zip'
OUT = '/home/antonio/Percorsi/linea_268_caselle_2025_stradale.gpx'
CACHE = '/home/antonio/Percorsi/.match_cache.json'
CHUNK = 10
STEP = CHUNK - 1  # 1 punto di sovrapposizione tra lotti consecutivi

COLORS = {
    '000268001H1': 'Blue',
    '000268001V1': 'DarkBlue',
    '000268002H2': 'Green',
    '000268002E2': 'DarkGreen',
    '000268002V2': 'Magenta',
}

with zipfile.ZipFile(SRC) as z:
    stops = list(csv.DictReader(io.StringIO(z.read('stops.txt').decode('utf-8'))))
    shapes = list(csv.DictReader(io.StringIO(z.read('shapes.txt').decode('utf-8'))))
    trips = list(csv.DictReader(io.StringIO(z.read('trips.txt').decode('utf-8'))))

shape_label = {}
for t in trips:
    sid = t['shape_id']
    if sid not in shape_label:
        dirn = 'Andata' if t['direction_id'] == '0' else 'Ritorno'
        shape_label[sid] = f"{dirn} - {t['trip_headsign']} ({sid})"

from collections import defaultdict
shape_points = defaultdict(list)
for p in shapes:
    shape_points[p['shape_id']].append(p)
for sid in shape_points:
    shape_points[sid].sort(key=lambda x: int(x['shape_pt_sequence']))

try:
    with open(CACHE) as f:
        cache = json.load(f)
except FileNotFoundError:
    cache = {}


def osrm_match(pts):
    coords = ';'.join(f"{p['shape_pt_lon']},{p['shape_pt_lat']}" for p in pts)
    url = f"https://router.project-osrm.org/match/v1/driving/{coords}?overview=full&geometries=geojson"
    req = urllib.request.Request(url, headers={'User-Agent': 'SmartTurnoArriva-route-snap/1.0'})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read())
    if data.get('code') != 'Ok':
        raise RuntimeError(data.get('code'))
    # concatena la geometria di tutti i "matchings" restituiti (a volte OSRM
    # spezza il lotto in piu' segmenti se perde traccia in un punto)
    coords_out = []
    for m in data['matchings']:
        coords_out += m['geometry']['coordinates']  # [lon, lat]
    return coords_out


matched_shapes = {}
total_shapes = len(shape_points)
for si, (sid, pts) in enumerate(shape_points.items(), 1):
    print(f"[{si}/{total_shapes}] {sid} ({shape_label.get(sid,sid)}) - {len(pts)} punti sorgente", flush=True)
    result = []
    i = 0
    chunk_idx = 0
    n_chunks = max(1, math.ceil((len(pts) - CHUNK) / STEP) + 1)
    while i < len(pts):
        chunk = pts[i:i+CHUNK]
        if len(chunk) < 2:
            break
        key = f"{sid}:{i}"
        if key in cache:
            geom = cache[key]
        else:
            try:
                geom = osrm_match(chunk)
            except Exception as e:
                print(f"    lotto {chunk_idx}/{n_chunks} FALLITO ({e}), uso punti originali", flush=True)
                geom = [[float(p['shape_pt_lon']), float(p['shape_pt_lat'])] for p in chunk]
            cache[key] = geom
            with open(CACHE, 'w') as f:
                json.dump(cache, f)
            time.sleep(0.35)
        if result and geom:
            geom = geom[1:]  # evita di duplicare il punto di sovrapposizione
        result += geom
        chunk_idx += 1
        if chunk_idx % 20 == 0:
            print(f"    lotto {chunk_idx}/{n_chunks}...", flush=True)
        i += STEP
    matched_shapes[sid] = result
    print(f"    -> {len(result)} punti dopo lo snap stradale", flush=True)

# --- snap delle fermate al punto piu' vicino tra tutte le tracce agganciate ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2-lat1)
    dlmb = math.radians(lon2-lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return 2*R*math.asin(math.sqrt(a))

all_matched_pts = []
for sid, geom in matched_shapes.items():
    all_matched_pts += [(lat, lon) for lon, lat in geom]

print(f"Snap di {len(stops)} fermate sul tracciato piu' vicino...", flush=True)
snapped_stops = []
for s in stops:
    slat, slon = float(s['stop_lat']), float(s['stop_lon'])
    best = min(all_matched_pts, key=lambda p: haversine(slat, slon, p[0], p[1]))
    dist = haversine(slat, slon, best[0], best[1])
    snapped_stops.append({**s, 'snap_lat': best[0], 'snap_lon': best[1], 'snap_dist': dist})
    print(f"  {s['stop_name'].strip():45s} spostata di {dist:.0f} m", flush=True)

# --- scrittura GPX finale ---
lines = []
lines.append('<?xml version="1.0" encoding="UTF-8"?>')
lines.append('<gpx version="1.1" creator="SmartTurnoArriva" xmlns="http://www.topografix.com/GPX/1/1" '
              'xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" '
              'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
              'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">')
lines.append('  <metadata>')
lines.append('    <name>Linea 268 Torino-Caselle Aeroporto (ARRIVA) - agganciata alle strade</name>')
lines.append('    <desc>Tracciato originale GTFS agganciato alla rete stradale via OSRM; fermate spostate sul tracciato piu vicino</desc>')
lines.append('  </metadata>')

for s in snapped_stops:
    name = escape(s['stop_name'].strip())
    lines.append(f'  <wpt lat="{s["snap_lat"]}" lon="{s["snap_lon"]}">')
    lines.append(f'    <name>{name}</name>')
    lines.append(f'    <cmt>Fermata {s["stop_code"]}</cmt>')
    lines.append(f'    <desc>stop_id {s["stop_id"]} - zona {s["zone_id"]} - spostata di {s["snap_dist"]:.0f}m dalla posizione originale</desc>')
    lines.append('    <sym>Bus Stop</sym>')
    lines.append('  </wpt>')

for sid, geom in matched_shapes.items():
    label = escape(shape_label.get(sid, sid))
    color = COLORS.get(sid, 'Red')
    lines.append('  <trk>')
    lines.append(f'    <name>{label}</name>')
    lines.append('    <extensions>')
    lines.append('      <gpxx:TrackExtension>')
    lines.append(f'        <gpxx:DisplayColor>{color}</gpxx:DisplayColor>')
    lines.append('      </gpxx:TrackExtension>')
    lines.append('    </extensions>')
    lines.append('    <trkseg>')
    for lon, lat in geom:
        lines.append(f'      <trkpt lat="{lat}" lon="{lon}"></trkpt>')
    lines.append('    </trkseg>')
    lines.append('  </trk>')

lines.append('</gpx>')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

import os
print(f"\nFatto: {OUT} ({os.path.getsize(OUT)} bytes)", flush=True)
