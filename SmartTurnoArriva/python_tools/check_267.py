import json

with open('/root/orari-app/data.js', 'r') as f:
    content = f.read()
    
    start_idx = content.find('[')
    end_idx = content.find('];') + 1
    
    json_str = content[start_idx:end_idx]
    
    try:
        db = json.loads(json_str)
        trips = [t for t in db if t.get('_linea') == '267']
        print(f"Found {len(trips)} trips for Linea 267")
        
        trip1004 = next((t for t in trips if t.get('PIOBESI T.SE-v.Torino 41-Capol') == '10:04' or t.get('PIOBESI T.SE-v.Torino/Costituz') == '10:05'), None)
        if trip1004:
            print("Trip 10:04 from Piobesi found:")
            print(json.dumps(trip1004, indent=2))
        else:
            print("Trip 10:04 not found in extracted data!")
    except Exception as e:
        print(f"Error parsing JSON: {e}")
