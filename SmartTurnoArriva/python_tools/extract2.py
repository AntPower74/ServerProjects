import pdfplumber
import json
import re

pdf_path = "/root/000275.pdf"

trips = []

# To group correctly, we can extract words and sort them
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        words = page.extract_words(x_tolerance=2, y_tolerance=2)
        
        # Group words by "line" (y-coordinate)
        lines = {}
        for w in words:
            # Round top coordinate to nearest 3 pixels to group them
            y = round(w['top'] / 3.0) * 3
            if y not in lines:
                lines[y] = []
            lines[y].append(w)
            
        # Sort lines from top to bottom
        sorted_y = sorted(lines.keys())
        
        page_trips = [] # list of dicts: trip_index -> {stop_name: time}
        
        # We need to find the column x-coordinates for trips.
        # Trips usually have times like "6.40" or "D" "R" "I"
        # Let's find rows that look like stops and collect times.
        
        # Let's first identify columns.
        # A good way is to just build a list of all X-coordinates of times.
        # But an easier way is: for each line, if it starts with a stop, the first few words are the stop name, 
        # and the subsequent words are times.
        
        stop_names = [
            "OULX - Stazione FS", "OULX - Liceo", "OULX - p.zza Garambois", "CESANA TORINESE",
            "SESTRIERE", "PRAGELATO", "FENESTRELLE - via Nazionale", "PEROSA ARG.-pzza Terzo Alpini (Arrivo)",
            "PEROSA ARG.-pzza Terzo Alpini (Partenza)", "PINASCA", "DUBBIONE - via Nazionale",
            "VILLAR PEROSA - via Nazionale", "S. GERMANO CHISONE", "PORTE", "S. MARTINO", "ABBADIA ALPINA",
            "PONTE LEMINA", "PINEROLO - piazza Cavour", "PINEROLO - movicentro (Arrivo)", 
            "PINEROLO - movicentro (Partenza)", "PINEROLO - c.so Torino-MACUMBA", "PINEROLO Centro Studi",
            "RIVA di Pinerolo", "Bivio BOTTEGHE", "AIRASCA", "NONE Bivio", "CANDIOLO IRCCS-Centro Ricerche",
            "STUPINIGI - Palazzina di Caccia", "TORINO - p.zza Carducci", 
            "TORINO -c.so V.Eman. II (Porta Nuova FS)", "TORINO - Autostazione c.so Bolzano"
        ]
        
        # We need to track the columns based on the first stop row we find.
        # Or better: build a matrix based on x0.
        
        for y in sorted_y:
            line_words = sorted(lines[y], key=lambda w: w['x0'])
            line_text = " ".join([w['text'] for w in line_words])
            
            # Find if this line matches a known stop
            matched_stop = None
            for s in stop_names:
                if line_text.startswith(s):
                    matched_stop = s
                    break
                    
            if matched_stop:
                # The words that are part of the stop name
                stop_name_len = len(matched_stop.replace(" ", ""))
                
                # We iterate over words. Once we pass the stop name, the rest are times.
                curr_len = 0
                time_words = []
                for w in line_words:
                    if curr_len >= stop_name_len:
                        time_words.append(w)
                    else:
                        curr_len += len(w['text'])
                
                # Ensure we only pick up actual times or valid tokens
                for w in time_words:
                    t = w['text']
                    if re.match(r'^(\d{1,2}[:.]\d{2}|[A-Z])$', t):
                        # Find which column this belongs to
                        # We define a column by roughly its x0 (within 10 pixels)
                        x = w['x0']
                        
                        # Find if we already have a trip in page_trips near this x
                        trip_found = False
                        for trip in page_trips:
                            if abs(trip['x'] - x) < 10:
                                trip['stops'][matched_stop] = t
                                trip_found = True
                                break
                        
                        if not trip_found:
                            page_trips.append({
                                'x': x,
                                'stops': {matched_stop: t}
                            })
                            
        # Now add these page_trips to global trips
        for trip in page_trips:
            # Only keep trips that have at least 2 valid stops (so it's an actual moving bus)
            if len(trip['stops']) > 1:
                trips.append(trip['stops'])

print("Total trips extracted:", len(trips))

# Now we generate the HTML directly here!
# We want a page where you pick "Partenza" and "Arrivo", and it lists all trips that go from A to B.

# Extract all unique stops that exist in the trips
all_valid_stops = set()
for t in trips:
    all_valid_stops.update(t.keys())
sorted_stops = sorted(list(all_valid_stops))

html_content = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ricerca Orari 275/282 (Da - A)</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        body {{
            font-family: 'Inter', sans-serif;
            background-color: #121214;
            color: #f0f0f2;
            margin: 0;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .container {{
            max-width: 600px;
            width: 100%;
            background: #1c1c1f;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border: 1px solid #2e2e34;
        }}
        h1 {{
            color: #06b6d4;
            margin-top: 0;
            text-align: center;
        }}
        .form-group {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        select {{
            width: 100%;
            padding: 1rem;
            background: #232328;
            border: 1px solid #2e2e34;
            color: white;
            border-radius: 8px;
            font-size: 1rem;
            outline: none;
        }}
        select:focus {{
            border-color: #06b6d4;
        }}
        .trip-card {{
            background: #232328;
            border: 1px solid #2e2e34;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .trip-time {{
            font-size: 1.5rem;
            font-weight: 800;
            color: #06b6d4;
        }}
        .trip-stations {{
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
        }}
        .trip-duration {{
            color: #a855f7;
            font-weight: 600;
            font-size: 0.9rem;
        }}
        .footer {{
            margin-top: 2rem;
            text-align: center;
            color: #9e9ea6;
            font-size: 0.8rem;
        }}
    </style>
</head>
<body>

<div class="container">
    <h1>Trova Corsa (Da - A)</h1>
    
    <div class="form-group">
        <div>
            <label style="color:#9e9ea6; font-size:0.9rem; margin-bottom:0.5rem; display:block;">Partenza da:</label>
            <select id="fromSelect" onchange="searchTrips()">
                <option value="">-- Seleziona Partenza --</option>
                {''.join([f'<option value="{k}">{k}</option>' for k in sorted_stops])}
            </select>
        </div>
        <div>
            <label style="color:#9e9ea6; font-size:0.9rem; margin-bottom:0.5rem; display:block;">Arrivo a:</label>
            <select id="toSelect" onchange="searchTrips()">
                <option value="">-- Seleziona Arrivo --</option>
                {''.join([f'<option value="{k}">{k}</option>' for k in sorted_stops])}
            </select>
        </div>
    </div>
    
    <div id="results"></div>
</div>

<div class="footer">Dati estratti automaticamente dal PDF ufficiale Arriva</div>

<script>
    const trips = {json.dumps(trips)};
    
    function parseTime(timeStr) {{
        if(!timeStr || timeStr.length < 4) return 0;
        let parts = timeStr.replace(".", ":").split(":");
        if(parts.length === 2) {{
            return parseInt(parts[0]) * 60 + parseInt(parts[1]);
        }}
        return 0;
    }}
    
    function searchTrips() {{
        const fromStop = document.getElementById('fromSelect').value;
        const toStop = document.getElementById('toSelect').value;
        const container = document.getElementById('results');
        container.innerHTML = '';
        
        if (!fromStop || !toStop) {{
            container.innerHTML = '<p style="text-align:center; color:#9e9ea6;">Seleziona sia la partenza che l\\'arrivo.</p>';
            return;
        }}
        if (fromStop === toStop) {{
            container.innerHTML = '<p style="text-align:center; color:#ef4444;">Partenza e arrivo non possono essere uguali.</p>';
            return;
        }}
        
        let validTrips = [];
        
        trips.forEach(trip => {{
            if (trip[fromStop] && trip[toStop]) {{
                // Check if time is valid numbers and 'from' is before 'to'
                let time1 = parseTime(trip[fromStop]);
                let time2 = parseTime(trip[toStop]);
                
                // If they are letters like 'D' or 'R', time1/2 will be 0.
                // We assume if both exist in the column, it's a valid trip. But we must check direction.
                // The order of stops in the array indicates direction. 
                // However, since we don't have the explicit array here, we can rely on time1 < time2 if they are numbers.
                // If they go past midnight (e.g. 23:50 to 00:20), time2 will be smaller. Let's handle that.
                if (time1 > 0 && time2 > 0) {{
                    if (time2 < time1 && time1 > 20*60 && time2 < 4*60) {{
                        time2 += 24*60; // add 24 hours
                    }}
                    
                    if (time1 < time2) {{
                        validTrips.push({{
                            fromTime: trip[fromStop].replace(".", ":"),
                            toTime: trip[toStop].replace(".", ":"),
                            time1: time1
                        }});
                    }}
                }} else {{
                    // Fallback for letter codes, just add them
                    validTrips.push({{
                        fromTime: trip[fromStop],
                        toTime: trip[toStop],
                        time1: 9999
                    }});
                }}
            }}
        }});
        
        // Sort by departure time
        validTrips.sort((a, b) => a.time1 - b.time1);
        
        if (validTrips.length === 0) {{
            container.innerHTML = '<p style="text-align:center; color:#9e9ea6;">Nessuna corsa trovata per questa tratta. Forse vanno nella direzione opposta.</p>';
            return;
        }}
        
        validTrips.forEach(t => {{
            const card = document.createElement('div');
            card.className = 'trip-card';
            
            card.innerHTML = `
                <div class="trip-stations">
                    <span style="color:#9e9ea6; font-size:0.85rem;">Partenza</span>
                    <span class="trip-time">${{t.fromTime}}</span>
                </div>
                <div class="trip-duration">
                    <span>&rarr;</span>
                </div>
                <div class="trip-stations" style="text-align: right;">
                    <span style="color:#9e9ea6; font-size:0.85rem;">Arrivo</span>
                    <span class="trip-time">${{t.toTime}}</span>
                </div>
            `;
            container.appendChild(card);
        }});
    }}
</script>

</body>
</html>
"""

output_path = "/root/.gemini/antigravity-cli/brain/4cdfeb15-664f-4107-a0ca-620778a57ac3/RicercaDaA.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Done")
