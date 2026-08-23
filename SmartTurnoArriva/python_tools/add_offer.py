import json

file_path = "/root/sito/offerte.json"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        offerte = json.load(f)
except Exception:
    offerte = []

nuova_offerta = {
    "title": "Tubo Multistrato Isocell ∅ 16x2mm Pert-al-pert Rotolo 25m Rosso",
    "price": "23,40",
    "newPrice": "23.40",
    "store": "Il Nostro Store",
    "expiration_date": "2030-12-31",
    "image_large": "http://217.154.200.184/tubo_rosso.jpg",
    "link": "http://217.154.200.184/#shop"
}

# Remove if exists to avoid duplicates
offerte = [o for o in offerte if "Tubo Multistrato" not in str(o.get('title', ''))]

# Insert at the top
offerte.insert(0, nuova_offerta)

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(offerte, f, indent=4, ensure_ascii=False)

print("Offerta aggiunta con successo a offerte.json")
