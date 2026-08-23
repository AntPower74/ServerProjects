import json
import time
import urllib.request
import urllib.parse

# 1. INSERISCI LA TUA API KEY DI GOOGLE QUI!
GOOGLE_API_KEY = "LA_TUA_API_KEY_GOOGLE_QUI"

def get_unique_stops():
    try:
        with open('/root/orari-app/data.js', 'r') as f:
            content = f.read()
            json_str = content[content.find('['):]
            if json_str.endswith(';'):
                json_str = json_str[:-1]
            db = json.loads(json_str)
            
            unique_stops = set()
            for trip in db:
                for key in trip.keys():
                    if not key.startswith('_'):
                        unique_stops.add(key)
            return unique_stops
    except Exception as e:
        print(f"Errore nella lettura di data.js: {e}")
        return set()

def geocode_google(stop_name):
    # Pulisce il nome per la ricerca (es. toglie i trattini per evitare errori)
    query = stop_name.replace('-', ' ')
    # Aggiungiamo un contesto geografico per evitare che Google trovi fermate in altre nazioni
    query = f"{query}, Piemonte, Italia"
    
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(query)}&key={GOOGLE_API_KEY}"
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            
            if data['status'] == 'OK' and len(data['results']) > 0:
                location = data['results'][0]['geometry']['location']
                return {"lat": location['lat'], "lng": location['lng']}
            else:
                print(f"Google non ha trovato: {stop_name} (Status: {data.get('status')})")
                return None
    except Exception as e:
        print(f"Errore di connessione per {stop_name}: {e}")
        return None

def main():
    if GOOGLE_API_KEY == "LA_TUA_API_KEY_GOOGLE_QUI":
        print("ERRORE: Devi prima inserire la tua GOOGLE_API_KEY nello script!")
        return

    unique_stops = get_unique_stops()
    print(f"Trovate {len(unique_stops)} fermate uniche. Inizio la ricerca su Google Maps API...")
    
    try:
        with open('/root/stops_coords.json', 'r') as f:
            coords_dict = json.load(f)
    except FileNotFoundError:
        coords_dict = {}

    count = 0
    for stop in unique_stops:
        # Salta quelle che abbiamo già correttamente nel file
        if stop in coords_dict and coords_dict[stop]:
            continue
            
        coords = geocode_google(stop)
        if coords:
            coords_dict[stop] = coords
            print(f"OK: {stop} -> {coords}")
            count += 1
        
        # Google Maps API accetta molte richieste, ma una piccola pausa evita blocchi
        time.sleep(0.1)

    with open('/root/stops_coords.json', 'w') as f:
        json.dump(coords_dict, f, indent=4)

    print(f"\nRicerca completata. Aggiunte {count} nuove coordinate esatte da Google.")

if __name__ == "__main__":
    main()
