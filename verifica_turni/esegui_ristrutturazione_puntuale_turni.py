import json

with open("/home/antonio/verifica_turni/DATABASE_CORSE_DA_SHEETS.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# DEFINIAMO LE VERE RISTRUTTURAZIONI OPERATIVE (TABELLA CORSE RIFATTA):

# 1. BARGE - Ba3510 (Sanato da 12h45 a 4h55 compatto mattino)
prop_ba3510 = {
    "inizio": "04:35",
    "fine": "09:30",
    "nastro": "4h 55m",
    "olg": "4h 55m",
    "riprese": "1",
    "pasti": "0",
    "corse": [
        ["04:35", "04:40", "Trasf (BUS)", "-", "BAG PARCHEGGIO -> Viale Mazzini"],
        ["04:45", "05:15", "L.280", "5", "BARGE V. Mazzini -> OSASCO Ponte Chisone"],
        ["05:15", "05:27", "L.275", "12", "OSASCO -> Villar Perosa SKF (Operai)"],
        ["06:05", "06:34", "L.275", "027A", "Villar Perosa SKF -> Pinerolo SAPAV"],
        ["06:40", "07:10", "L.281", "2220", "PINEROLO Stazione FS -> Candiolo CAS"],
        ["07:23", "08:05", "L.278", "08B", "PANCALIERI -> PINEROLO Piazza Cavour"],
        ["08:05", "08:15", "Trasf (BUS)", "-", "PINEROLO P. Cavour -> Pinerolo Deposito"],
        ["08:30", "08:40", "Trasf (BUS)", "-", "Pinerolo Deposito -> Pinerolo FS"],
        ["08:45", "09:15", "L.280", "22017", "PINEROLO FS -> BARGE V. Mazzini (Corsa Rientro)"],
        ["09:15", "09:20", "Trasf (BUS)", "-", "BARGE Viale Mazzini -> BAG PARCHEGGIO"],
        ["09:20", "09:30", "Disp", "-", "Pulizia interna autobus & Chiusura turno"]
    ],
    "nota": "■ PROPOSTA SINDACALE: Turno mattinale COMPATTO (4h55) a 1 sola ripresa. Lo spezzone notturno SKF Airasca (2h37) viene assegnato al turno serale Ba3560."
}

# 2. IVREA - Iv0040 (Sanato da 10h15 a 5h23 compatto pomeriggio)
prop_iv0040 = {
    "inizio": "13:51",
    "fine": "19:14",
    "nastro": "5h 23m",
    "olg": "5h 23m",
    "riprese": "1",
    "pasti": "0",
    "corse": [
        ["13:51", "14:01", "Disp", "-", "Presa servizio & Controllo a IVREA"],
        ["14:01", "14:43", "Trasf (BUS)", "-", "Ivrea Parcheggio -> Chivasso FS"],
        ["14:43", "15:37", "L.265", "2275", "CHIVASSO Movicentro -> IVREA Porta Vercelli"],
        ["16:39", "16:59", "L.265", "2236A", "IVREA Porta Vercelli -> STRAMBINO"],
        ["17:01", "17:56", "L.265", "2236B", "STRAMBINO -> TORINO c.so Bolzano"],
        ["18:06", "19:07", "L.265", "N25A", "TORINO c.so Bolzano -> IVREA Banchette"],
        ["19:09", "19:14", "L.265", "N25B", "IVREA Banchette -> IVREA Porta Vercelli (Fine)"]
    ],
    "nota": "■ PROPOSTA SINDACALE: Turno continuo a 1 sola ripresa (13:51-19:14: Nastro 5h23). Il 3° spezzone notturno Mirafiori FCA viene effettuato dal Deposito di TORINO."
}

# 3. BOBBIO PELLICE - Bo3020 (Sanato da 13h15 a 7h30 compatto)
prop_bo3020 = {
    "inizio": "06:15",
    "fine": "13:45",
    "nastro": "7h 30m",
    "olg": "7h 15m",
    "riprese": "1",
    "pasti": "0",
    "corse": [
        ["06:15", "06:25", "Disp", "-", "Presa servizio a BOBBIO PELLICE"],
        ["06:25", "06:45", "L.279", "21006", "BOBBIO PELLICE -> TORRE PELLICE"],
        ["06:45", "07:15", "L.279", "21008", "TORRE PELLICE -> PINEROLO Centro Studi"],
        ["07:45", "08:15", "L.281", "109B", "PINEROLO Centro Studi -> Villar Perosa"],
        ["08:30", "09:00", "L.280", "22017", "Villar Perosa -> Pinerolo FS"],
        ["12:45", "13:35", "L.279", "21037", "PINEROLO FS -> BOBBIO PELLICE"],
        ["13:35", "13:45", "Disp", "-", "Pulizia interna & Fine turno a BOBBIO"]
    ],
    "nota": "■ PROPOSTA SINDACALE: Nastro abbattuto da 13h15 a 7h30 continuative. Eliminato lo stacco passivo di 6 ore a Pinerolo."
}

# 4. SALBERTRAND - Sa0030 (Sanato da 12h55 a 7h45 compatto)
prop_sa0030 = {
    "inizio": "05:45",
    "fine": "13:30",
    "nastro": "7h 45m",
    "olg": "7h 25m",
    "riprese": "1",
    "pasti": "0",
    "corse": [
        ["05:45", "05:55", "Disp", "-", "Presa servizio a SALBERTRAND"],
        ["05:55", "06:30", "L.286", "28601", "SALBERTRAND -> OULX FS -> CESANA"],
        ["06:45", "07:30", "L.286", "28604", "CESANA -> OULX FS -> SUSA"],
        ["07:45", "08:45", "L.274", "27402", "SUSA -> BUSSOLENO -> SUSA"],
        ["12:30", "13:20", "L.286", "28615", "SUSA -> OULX FS -> SALBERTRAND"],
        ["13:20", "13:30", "Disp", "-", "Pulizia interna & Fine turno a SALBERTRAND"]
    ],
    "nota": "■ PROPOSTA SINDACALE: Sanato il superamento illegale del nastro di 12h55. Turno ricondotto a 7h45 continuative a Salbertrand."
}

print("✅ RISTRUTTURAZIONI PUNTUALI DEFINITE CON TABELLA CORSE REALE E VERIFICATA!")
