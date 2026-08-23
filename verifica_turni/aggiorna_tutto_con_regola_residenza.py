import json

# 1. Aggiorna motore_ottimo_globale_ortools.py
with open("/home/antonio/verifica_turni/motore_ottimo_globale_ortools.py", "r") as f:
    code_ortools = f.read()

# 2. Aggiorna web/index.html con la funzione calcolaOLGRetribuito e card sosta dettagliata
with open("/home/antonio/verifica_turni/web/index.html", "r") as f:
    html = f.read()

# Sostituiamo la logica in index.html
js_olg_func = r'''
        // CALCOLO OLG RETRIBUITO CCNL (Soste <=30m al 100%, eccedenza 0% in residenza, 12% fuori residenza)
        function calcolaOLGRetribuito(t) {
            const depPrefix = (t.codice_turno || '').substring(0, 2).toLowerCase();
            const depNome = (t.deposito || '').toLowerCase();
            
            const depMap = {
                'to': ['torino', 'c.so bolzano', 'bolzano'],
                'pi': ['pinerolo'],
                'pe': ['perosa'],
                'pt': ['pont st. martin', 'pont saint martin', 'pont'],
                'su': ['susa'],
                'pb': ['piobesi'],
                'ca': ['caselle'],
                'sa': ['salbertrand'],
                'lu': ['luserna'],
                'ba': ['barge'],
                'iv': ['ivrea'],
                'bo': ['bobbio pellice', 'bobbio']
            };
            
            const keywords = depMap[depPrefix] || [depNome];
            if (depNome && !keywords.includes(depNome)) keywords.push(depNome);
            
            let totMinuti = 0;
            const att = t.attivita || [];
            
            for (let a of att) {
                const pM = parseClock(a.partenza);
                const arrM = parseClock(a.arrivo);
                const dur = arrM >= pM ? (arrM - pM) : (1440 - pM + arrM);
                
                const isSosta = (a.linea === 'Sosta') || a.is_sosta_deposito;
                if (!isSosta) {
                    totMinuti += dur;
                } else {
                    const desc = ((a.descrizione || '') + ' ' + (a.da || '') + ' ' + (a.a || '')).toLowerCase();
                    const isInResidenza = keywords.some(k => k && desc.includes(k));
                    
                    if (dur <= 30) {
                        totMinuti += dur;
                    } else {
                        totMinuti += 30;
                        const ecc = dur - 30;
                        if (!isInResidenza) {
                            totMinuti += ecc * 0.12;
                        }
                    }
                }
            }
            return Math.round(totMinuti);
        }
'''

# Inseriamo la funzione in index.html prima di aggiornaFiltriCondizioni
if "function calcolaOLGRetribuito" not in html:
    html = html.replace("function verificaSosteEntro6h(t) {", js_olg_func + "\n        function verificaSosteEntro6h(t) {")

# Aggiorniamo la parte in cui olgM viene calcolato
html = html.replace(
    "const olgM = t.olg_m || parseDurataM(t.olg_str) || parseDurataM(t.ore_lavoro);",
    "const olgM = calcolaOLGRetribuito(t);"
)

with open("/home/antonio/verifica_turni/web/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ index.html aggiornato con calcolaOLGRetribuito() dinamico.")
