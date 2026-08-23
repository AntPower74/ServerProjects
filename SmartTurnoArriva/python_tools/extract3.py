import json

# Read the previously extracted trips from extract2.py
# Wait, I didn't save them to a json. I just embedded them into the html string in extract2.py.
# But wait, in extract2.py I had `trips`. I'll just re-run the extraction logic, or simply copy the extraction logic.
import pdfplumber
import re

pdf_path = "/root/000275.pdf"

trips = []

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        words = page.extract_words(x_tolerance=2, y_tolerance=2)
        lines = {}
        for w in words:
            y = round(w['top'] / 3.0) * 3
            if y not in lines:
                lines[y] = []
            lines[y].append(w)
            
        sorted_y = sorted(lines.keys())
        page_trips = []
        
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
        
        for y in sorted_y:
            line_words = sorted(lines[y], key=lambda w: w['x0'])
            line_text = " ".join([w['text'] for w in line_words])
            
            matched_stop = None
            for s in stop_names:
                if line_text.startswith(s):
                    matched_stop = s
                    break
                    
            if matched_stop:
                stop_name_len = len(matched_stop.replace(" ", ""))
                curr_len = 0
                time_words = []
                for w in line_words:
                    if curr_len >= stop_name_len:
                        time_words.append(w)
                    else:
                        curr_len += len(w['text'])
                
                for w in time_words:
                    t = w['text']
                    if re.match(r'^(\d{1,2}[:.]\d{2}|[A-Z])$', t):
                        x = w['x0']
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
                            
        for trip in page_trips:
            if len(trip['stops']) > 1:
                trips.append(trip['stops'])

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
        .clock-container {{
            text-align: center;
            margin-bottom: 2rem;
            background: #232328;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #2e2e34;
        }}
        #clock-time {{
            font-size: 2rem;
            font-weight: 800;
            color: #06b6d4;
            margin-bottom: 0.2rem;
        }}
        #clock-date {{
            color: #9e9ea6;
            font-size: 0.9rem;
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
            transition: all 0.3s;
        }}
        .trip-card.next-bus {{
            border: 2px solid #10b981;
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
            background: rgba(16, 185, 129, 0.05);
            position: relative;
        }}
        .next-bus-badge {{
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
            background: #10b981;
            color: #fff;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 1px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .trip-time {{
            font-size: 1.5rem;
            font-weight: 800;
            color: #f0f0f2;
        }}
        .next-bus .trip-time {{
            color: #10b981;
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
            text-align: center;
        }}
        .trip-duration small {{
            display: block;
            font-size: 0.7rem;
            opacity: 0.8;
            margin-top: 2px;
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
    <div class="clock-container">
        <div id="clock-time">--:--:--</div>
        <div id="clock-date">Caricamento data...</div>
    </div>

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
    
    function updateClock() {{
        const now = new Date();
        const timeString = now.toLocaleTimeString('it-IT');
        const dateString = now.toLocaleDateString('it-IT', {{ weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }});
        
        document.getElementById('clock-time').textContent = timeString;
        document.getElementById('clock-date').textContent = dateString.charAt(0).toUpperCase() + dateString.slice(1);
        
        // Auto-refresh search to update the "next bus" badge if time changes
        if(document.getElementById('results').innerHTML !== '') {{
            searchTrips();
        }}
    }}
    
    setInterval(updateClock, 15000); // refresh every 15 seconds
    updateClock(); // initial call
    
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
                let time1 = parseTime(trip[fromStop]);
                let time2 = parseTime(trip[toStop]);
                
                if (time1 > 0 && time2 > 0) {{
                    if (time2 < time1 && time1 > 20*60 && time2 < 4*60) {{
                        time2 += 24*60; 
                    }}
                    
                    if (time1 < time2) {{
                        validTrips.push({{
                            fromTime: trip[fromStop].replace(".", ":"),
                            toTime: trip[toStop].replace(".", ":"),
                            time1: time1,
                            time2: time2
                        }});
                    }}
                }} else {{
                    validTrips.push({{
                        fromTime: trip[fromStop],
                        toTime: trip[toStop],
                        time1: 9999,
                        time2: 9999
                    }});
                }}
            }}
        }});
        
        validTrips.sort((a, b) => a.time1 - b.time1);
        
        if (validTrips.length === 0) {{
            container.innerHTML = '<p style="text-align:center; color:#9e9ea6;">Nessuna corsa trovata per questa tratta. Forse vanno nella direzione opposta.</p>';
            return;
        }}
        
        // Find the next bus
        const now = new Date();
        const currentMinutes = now.getHours() * 60 + now.getMinutes();
        
        let nextBusIndex = -1;
        for (let i = 0; i < validTrips.length; i++) {{
            if (validTrips[i].time1 > currentMinutes && validTrips[i].time1 !== 9999) {{
                nextBusIndex = i;
                break;
            }}
        }}
        
        // If all buses for today have passed, maybe the first one tomorrow is next
        if (nextBusIndex === -1 && validTrips.length > 0 && validTrips[0].time1 !== 9999) {{
            nextBusIndex = 0; // The first one tomorrow
        }}
        
        validTrips.forEach((t, index) => {{
            const card = document.createElement('div');
            card.className = 'trip-card' + (index === nextBusIndex ? ' next-bus' : '');
            
            let badgeHtml = index === nextBusIndex ? '<div class="next-bus-badge">PROSSIMA CORSA</div>' : '';
            
            let durationHtml = '';
            if (t.time1 !== 9999) {{
                let durationMins = t.time2 - t.time1;
                let h = Math.floor(durationMins / 60);
                let m = durationMins % 60;
                let durText = h > 0 ? h + "h " + m + "m" : m + "m";
                durationHtml = `<span>&rarr;</span><small>${{durText}}</small>`;
            }} else {{
                durationHtml = `<span>&rarr;</span>`;
            }}
            
            card.innerHTML = badgeHtml + `
                <div class="trip-stations">
                    <span style="color:#9e9ea6; font-size:0.85rem;">Partenza</span>
                    <span class="trip-time">${{t.fromTime}}</span>
                </div>
                <div class="trip-duration">
                    ${{durationHtml}}
                </div>
                <div class="trip-stations" style="text-align: right;">
                    <span style="color:#9e9ea6; font-size:0.85rem;">Arrivo</span>
                    <span class="trip-time">${{t.toTime}}</span>
                </div>
            `;
            container.appendChild(card);
        }});
        
        // Scroll to the next bus so it's in view
        if (nextBusIndex !== -1) {{
             setTimeout(() => {{
                  const nextCard = container.querySelector('.next-bus');
                  if(nextCard) {{
                      nextCard.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                  }}
             }}, 100);
        }}
    }}
</script>

</body>
</html>
"""

output_path = "/root/.gemini/antigravity-cli/brain/4cdfeb15-664f-4107-a0ca-620778a57ac3/RicercaLive.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Done")
