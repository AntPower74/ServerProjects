import json
import os

with open("/root/orari_275.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Sort times and remove duplicates for each stop, filter out letters
clean_data = {}
for stop, times in data.items():
    # Only keep proper times (e.g. 6.40, 15:20) and convert . to :
    valid_times = []
    for t in times:
        t = t.replace(".", ":")
        if ":" in t:
            parts = t.split(":")
            if len(parts[0]) == 1: parts[0] = "0" + parts[0]
            valid_times.append(f"{parts[0]}:{parts[1]}")
    
    unique_times = sorted(list(set(valid_times)))
    if unique_times:
        clean_data[stop] = unique_times

html_content = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ricerca Orari Linea 275/282</title>
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
        select, input {{
            width: 100%;
            padding: 1rem;
            margin-bottom: 1.5rem;
            background: #232328;
            border: 1px solid #2e2e34;
            color: white;
            border-radius: 8px;
            font-size: 1.1rem;
            outline: none;
        }}
        select:focus, input:focus {{
            border-color: #06b6d4;
        }}
        .times-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
            gap: 10px;
        }}
        .time-badge {{
            background: rgba(6, 182, 212, 0.15);
            color: #06b6d4;
            border: 1px solid rgba(6, 182, 212, 0.3);
            padding: 0.5rem;
            border-radius: 6px;
            text-align: center;
            font-weight: 600;
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
    <h1>Ricerca Orari 275/282</h1>
    <p style="text-align: center; color: #9e9ea6; margin-bottom: 2rem;">Seleziona la tua fermata per vedere tutti gli orari di passaggio estratti dal PDF.</p>
    
    <select id="stopSelect" onchange="showTimes()">
        <option value="">-- Seleziona una fermata --</option>
        {''.join([f'<option value="{k}">{k}</option>' for k in sorted(clean_data.keys())])}
    </select>
    
    <div id="results" class="times-grid"></div>
</div>

<div class="footer">Dati estratti automaticamente dal PDF ufficiale Arriva</div>

<script>
    const orari = {json.dumps(clean_data)};
    
    function showTimes() {{
        const stop = document.getElementById('stopSelect').value;
        const container = document.getElementById('results');
        container.innerHTML = '';
        
        if (stop && orari[stop]) {{
            orari[stop].forEach(time => {{
                const div = document.createElement('div');
                div.className = 'time-badge';
                div.textContent = time;
                container.appendChild(div);
            }});
        }}
    }}
</script>

</body>
</html>
"""

# Saving as artifact
output_path = "/root/.gemini/antigravity-cli/brain/4cdfeb15-664f-4107-a0ca-620778a57ac3/RicercaOrari275.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

# create a markdown wrapper artifact so they can click it directly in the UI if needed
md_path = "/root/.gemini/antigravity-cli/brain/4cdfeb15-664f-4107-a0ca-620778a57ac3/Orari275.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write(f"Ho creato il file di ricerca!\n\nClicca qui per aprirlo e usarlo: [RicercaOrari275.html](file://{output_path})\n\n*(Puoi anche scaricare questo file HTML sul tuo computer e usarlo offline)*")

print("Done")
