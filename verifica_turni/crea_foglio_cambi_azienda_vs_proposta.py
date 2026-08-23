import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = "1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM"
creds_path = "/home/antonio/verifica_turni/credentials.json"

scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials = Credentials.from_service_account_file(creds_path, scopes=scopes)
gc = gspread.authorize(credentials)
sh = gc.open_by_key(SPREADSHEET_ID)

# Creazione o apertura foglio "CONFRONTO_CAMBI_TURNO"
try:
    ws = sh.worksheet("CONFRONTO_CAMBI_TURNO")
except:
    ws = sh.add_worksheet(title="CONFRONTO_CAMBI_TURNO", rows=100, cols=15)

ws.clear()

dati_cambi = [
    ["🔄 CONFRONTO STRUTTURATO DEI CAMBI TURNO: AZIENDA 2026 vs NOSTRA PROPOSTA", "", "", "", "", "", ""],
    ["", "", "", "", "", "", ""],
    ["1. RIEPILOGO STATISTICO GENERALE DEI CAMBI SUL POSTO", "", "", "", "", "", ""],
    ["Ambito / Nodo di Interscambio", "Cambi Previsti da Azienda 2026", "Cambi Nostra Proposta", "Mezzo Azienda", "Mezzo Nostra Proposta", "Impatto Operativo / Delta"],
    [
        "Torino Centro (Piazza Carlo Felice)", 
        "0 (Nessun cambio: bus rientra a vuoto a Grugliasco)", 
        "8 cambi sul posto a rotazione continua", 
        "Autobus a vuoto nel traffico (16 km A/R)", 
        "Passaggio bus sul posto + Auto Aziendale", 
        "🟢 Eliminati 16 viaggi a vuoto/giorno Torino Centro-Grugliasco"
    ],
    [
        "Torino Porta Susa (Corso Bolzano)", 
        "2 cambi disarticolati", 
        "6 cambi strutturati a cadenzamento orario", 
        "Attese passive non retribuite fino a 2h30", 
        "Auto di Servizio Aziendale", 
        "🟢 Abbattuti i nastri lunghi da 11h/12h a 7h30/8h00"
    ],
    [
        "Pinerolo (Movicentro / Centro Studi)", 
        "Cambi con stacco lungo e sosta passiva", 
        "Cambi e coincidenze dirette con linee valli", 
        "Bus fermo passivo a Pinerolo", 
        "Autobus in linea passeggeri 000280", 
        "🟢 Rientro garantito a Barge/Luserna senza stacchi"
    ],
    ["", "", "", "", "", "", ""],
    ["2. DETTAGLIO PUNTUALE DEI CAMBI TURNO - NOSTRA PROPOSTA", "", "", "", "", "", ""],
    ["Nodo di Cambio", "Orario Cambio", "Turno Smontante (Cede)", "Turno Montante (Riceve)", "Mezzo Trasferimento", "Linea / Destinazione Corsa", "Vantaggio Principale"],
    
    # CARLO FELICE
    ["Piazza Carlo Felice", "11:00", "To0270", "To0310", "Auto Aziendale", "Linea 000268 per Caselle Aeroporto", "Smonto puntuale To0270 a 7h15"],
    ["Piazza Carlo Felice", "11:45", "To0280", "To0710", "Auto Aziendale", "Linea 000119 / 000277 per Airasca SKF", "Smonto To0280 alle 12:40 senza buco passivo"],
    ["Piazza Carlo Felice", "12:15", "To0290", "To0320", "Auto Aziendale", "Linea 000268 per Caselle Aeroporto", "Bus rimane in servizio commerciale continuo"],
    ["Piazza Carlo Felice", "12:45", "To0295", "To0330", "Auto Aziendale", "Linea 000268 per Caselle Aeroporto", "Evitato viaggio a vuoto a Grugliasco a mezzogiorno"],
    ["Piazza Carlo Felice", "13:15", "To0300", "To0330", "Auto Aziendale", "Linea 000268 per Caselle Aeroporto", "Cadenzamento perfetto navetta aeroporto"],
    ["Piazza Carlo Felice", "15:45", "To0310", "To0340", "Auto Aziendale", "Linea 000268 per Caselle Aeroporto", "Copertura orario di punta pomeridiano"],
    ["Piazza Carlo Felice", "16:45", "To0330", "To0350", "Auto Aziendale", "Linea 000268 per Caselle Aeroporto", "Rotazione pulita senza straordinario"],
    ["Piazza Carlo Felice", "18:15", "To0320", "To0360", "Auto Aziendale (Andata) / Bus (Notturno)", "Linea 000268 notturna con corsa passeggeri 00:00", "Zero vuoti notturni da Caselle a Grugliasco"],

    # PORTA SUSA
    ["Porta Susa (c.so Bolzano)", "09:30", "To0610", "To0650", "Auto di Servizio Aziendale", "Servizio urbano/suburbano Torino", "Abbattuto nastro To0610 da 11h15 a 7h20"],
    ["Porta Susa (c.so Bolzano)", "09:30", "To0620", "To0660", "Auto di Servizio Aziendale", "Servizio Speciale 40h Lun-Ven", "Attivato Turno 40h To0660 a 8h00 (Sab+Dom libero)"],
    ["Porta Susa (c.so Bolzano)", "12:45", "To0700", "To0670", "Auto di Servizio Aziendale", "Linea industriale Skf / Airasca", "Eliminato buco passivo di 2h18 a metà giornata"],
    ["Porta Susa (c.so Bolzano)", "15:40", "To0650", "To0710", "Auto di Servizio Aziendale", "Servizio di punta pomeridiana", "Smonto regolare To0650 a nastro compatto"],
    ["Porta Susa (c.so Bolzano)", "17:00", "To0660", "To0640", "Auto di Servizio Aziendale", "Servizio serale Torino", "Chiusura 8h00 per To0660 (40h settimanali)"],
    ["Porta Susa (c.so Bolzano)", "18:30", "To0670", "To1040", "Auto di Servizio Aziendale", "Rientro serale Torino", "Nastro compatto per To0670"]
]

ws.update(range_name=f'A1:G{len(dati_cambi)}', values=dati_cambi)
print("✅ FOGLIO 'CONFRONTO_CAMBI_TURNO' CREATO E POPOLATO CON SUCCESSO SU GOOGLE SHEETS!")
