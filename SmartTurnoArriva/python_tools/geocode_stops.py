import json
import time
import urllib.request
import urllib.parse
import re

# Read data.js to get all unique stops
try:
    with open('/root/orari-app/data.js', 'r') as f:
        content = f.read()
        # Find the window.db = [...] part
        json_str = content[content.find('['):]
        # It might have a trailing semicolon
        if json_str.endswith(';'):
            json_str = json_str[:-1]
        
        db = json.loads(json_str)
except Exception as e:
    print(f"Error reading data.js: {e}")
    db = []

unique_stops = set()
for trip in db:
    for key in trip.keys():
        if not key.startswith('_'):
            unique_stops.add(key)

print(f"Found {len(unique_stops)} unique stops. Geocoding via Nominatim...")

coords_dict = {}

def geocode_stop(stop_name):
    # Clean up the name for better geocoding results
    search_query = stop_name.split(' - ')[0] # e.g. "PINEROLO - piazza Cavour" -> "PINEROLO"
    # Actually, the specific address like "piazza Cavour" is better. Let's keep it but remove dashes
    search_query = stop_name.replace('-', ' ')
    search_query += " Piemonte Italy"
    
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(search_query)}&format=json&limit=1"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'ArrivaMove/1.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            if data:
                return {"lat": float(data[0]['lat']), "lng": float(data[0]['lon'])}
    except Exception as e:
        print(f"Failed to geocode {stop_name}: {e}")
    
    # Try just the city name if the full string fails
    city_only = stop_name.split(' - ')[0] + " Piemonte Italy"
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(city_only)}&format=json&limit=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'ArrivaMove/1.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            if data:
                return {"lat": float(data[0]['lat']), "lng": float(data[0]['lon'])}
    except:
        pass
        
    return None

count = 0
for stop in unique_stops:
    coords = geocode_stop(stop)
    if coords:
        coords_dict[stop] = coords
        print(f"OK: {stop} -> {coords}")
    else:
        print(f"FAIL: {stop}")
    
    # Be nice to Nominatim (1 request per second)
    time.sleep(1.2)

with open('/root/stops_coords.json', 'w') as f:
    json.dump(coords_dict, f, indent=4)

print(f"Geocoding complete. Saved {len(coords_dict)} coordinates out of {len(unique_stops)} stops.")
