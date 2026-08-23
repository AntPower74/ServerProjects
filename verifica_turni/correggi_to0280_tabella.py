# La tabella di destra di To0280 DEVE contenere esplicitamente il CAMBIO e il Trasf (AUTO)
corse_prop_to0280 = [
    ["05:05", "05:15", "Disp", "-", "Presa servizio & Controllo livelli a Grugliasco"],
    ["05:15", "05:45", "Trasf (BUS)", "-", "TORINO DEPOSITO -> TO piazza Carlo Felice"],
    ["05:45", "06:30", "L.268", "A5", "TO piazza Carlo Felice -> CASELLE Aeroporto"],
    ["07:00", "07:45", "L.268", "A122", "CASELLE Aeroporto -> TO piazza Carlo Felice"],
    ["08:00", "08:37", "L.268", "D7", "TO piazza Carlo Felice -> CASELLE Aeroporto"],
    ["09:00", "09:45", "L.268", "A30", "CASELLE Aeroporto -> TO piazza Carlo Felice"],
    ["10:00", "10:37", "L.268", "D15", "TO piazza Carlo Felice -> CASELLE Aeroporto"],
    ["11:00", "11:45", "L.268", "A38", "CASELLE Aeroporto -> TO piazza Carlo Felice"],
    ["11:45", "12:00", "CAMBIO", "-", "CAMBIO CARLO FELICE -> CEDE IL BUS A To0710"],
    ["12:00", "12:30", "Trasf (AUTO)", "-", "Rientro a TORINO DEPOSITO in AUTO AZIENDALE"],
    ["12:30", "12:40", "Disp", "-", "Pulizia finale & Chiusura turno a Grugliasco"]
]

print("Tabella To0280 corretta con CAMBIO e AUTO AZIENDALE espliciti!")
