import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = "1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM"
creds_path = "/home/antonio/verifica_turni/credentials.json"

scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials = Credentials.from_service_account_file(creds_path, scopes=scopes)
gc = gspread.authorize(credentials)
sh = gc.open_by_key(SPREADSHEET_ID)

ws = sh.worksheet("CONFRONTO_CAMBI_TURNO")
ws.clear()

dati_cambi_completi = [
    ["🔄 CONFRONTO STRUTTURATO DEI CAMBI TURNO: AZIENDA 2026 vs NOSTRA PROPOSTA (TUTTI I DEPOSITI)", "", "", "", "", "", ""],
    ["", "", "", "", "", "", ""],
    ["1. QUADRO GENERALE DEI NODI DI CAMBIO E GESTIONE MEZZI PER DEPOSITO", "", "", "", "", "", ""],
    ["Deposito / Area Territoriale", "Cambi Azienda 2026", "Cambi Nostra Proposta", "Punti di Cambio / Interscambio", "Mezzo Utilizzato", "Impatto Operativo & Risparmio"],
    [
        "TORINO (Grugliasco)", 
        "2 cambi disarticolati", 
        "14 cambi sincronizzati", 
        "Piazza Carlo Felice (8) & Porta Susa (6)", 
        "Auto Aziendale + Passaggio Bus", 
        "🟢 Eliminati 16 vuoti/giorno Torino-Grugliasco; abbattuti nastri a 7h30/8h00"
    ],
    [
        "PINEROLO & VALLI (Perosa, Luserna, Bobbio, Barge)", 
        "Cambi isolati con lunghe soste passive", 
        "8 cambi e rotazioni continue", 
        "Pinerolo Movicentro, Centro Studi, Perosa Deposito", 
        "Bus di linea passeggeri (000280 / 000275) + Coincidenze", 
        "🟢 Eliminati stacchi da 3h-4h non pagati; rientri garantiti a fine turno"
    ],
    [
        "VALLE DI SUSA (Susa & Salbertrand)", 
        "0 cambi (Nastri illegali fino a 12h55)", 
        "4 cambi e staffette sul posto", 
        "Susa Deposito, Oulx FS, Bardonecchia, Cesana", 
        "Bus in coincidenza di linea + Mezzo di staffetta", 
        "🟢 Sanata violazione 12h55 su Sa0030 e paghe da 5h00 a Susa"
    ],
    [
        "VALLE D'AOSTA (Pont Saint Martin & Ivrea)", 
        "0 cambi (Soste passive ad Aosta fino a 75m)", 
        "3 cambi / rotazioni sul posto", 
        "Aosta Autostazione, Pont Saint Martin, Ivrea Movicentro", 
        "Bus in linea passeggeri continua", 
        "🟢 Eliminati buchi passivi ad Aosta; turni compatti a 7h30"
    ],
    [
        "PIOBESI TORINESE", 
        "10 turni con vuoti bus a Piobesi", 
        "Rotazione con rifornimento protetto", 
        "Beinasco CNG (Stazione Metano/Gasolio)", 
        "Autobus a fine corsa passeggeri", 
        "🟢 Zero vuoti bus per Piobesi; risparmio netto € 17.779,65/anno"
    ],
    ["", "", "", "", "", "", ""],
    ["2. DETTAGLIO PUNTUALE DEI CAMBI TURNO PER TUTTI I DEPOSITI - NOSTRA PROPOSTA", "", "", "", "", "", ""],
    ["Deposito / Territorio", "Nodo di Cambio", "Orario Cambio", "Turno Smontante (Cede)", "Turno Montante (Riceve)", "Mezzo Trasferimento", "Linea / Destinazione / Vantaggio"],
    
    # TORINO - CARLO FELICE
    ["TORINO", "Piazza Carlo Felice", "11:00", "To0270", "To0310", "Auto Aziendale", "Linea 000268 per Caselle -> Smonto To0270 a 7h15"],
    ["TORINO", "Piazza Carlo Felice", "11:45", "To0280", "To0710", "Auto Aziendale", "Linea 000119/277 Airasca SKF -> Smonto To0280 a 12:40"],
    ["TORINO", "Piazza Carlo Felice", "12:15", "To0290", "To0320", "Auto Aziendale", "Linea 000268 per Caselle -> Bus resta in linea continua"],
    ["TORINO", "Piazza Carlo Felice", "12:45", "To0295", "To0330", "Auto Aziendale", "Linea 000268 per Caselle -> Zero vuoti a mezzogiorno"],
    ["TORINO", "Piazza Carlo Felice", "13:15", "To0300", "To0330", "Auto Aziendale", "Linea 000268 per Caselle -> Cadenzamento regolare"],
    ["TORINO", "Piazza Carlo Felice", "15:45", "To0310", "To0340", "Auto Aziendale", "Linea 000268 per Caselle -> Punta pomeridiana"],
    ["TORINO", "Piazza Carlo Felice", "16:45", "To0330", "To0350", "Auto Aziendale", "Linea 000268 per Caselle -> Rotazione pulita"],
    ["TORINO", "Piazza Carlo Felice", "18:15", "To0320", "To0360", "Auto Aziendale (And.) / Bus (Notturno)", "Linea 000268 notturna -> Rientro corsa passeggeri 00:00"],

    # TORINO - PORTA SUSA
    ["TORINO", "Porta Susa (c.so Bolzano)", "09:30", "To0610", "To0650", "Auto di Servizio Aziendale", "Nastro To0610 abbattuto da 11h15 a 7h20"],
    ["TORINO", "Porta Susa (c.so Bolzano)", "09:30", "To0620", "To0660", "Auto di Servizio Aziendale", "Turno Speciale 40h To0660 a 8h00 (Sab+Dom libero)"],
    ["TORINO", "Porta Susa (c.so Bolzano)", "12:45", "To0700", "To0670", "Auto di Servizio Aziendale", "Eliminato stacco passivo di 2h18 a metà turno"],
    ["TORINO", "Porta Susa (c.so Bolzano)", "15:40", "To0650", "To0710", "Auto di Servizio Aziendale", "Smonto compatto To0650 nel pomeriggio"],
    ["TORINO", "Porta Susa (c.so Bolzano)", "17:00", "To0660", "To0640", "Auto di Servizio Aziendale", "Chiusura 8h00 To0660 (40h settimanali)"],
    ["TORINO", "Porta Susa (c.so Bolzano)", "18:30", "To0670", "To1040", "Auto di Servizio Aziendale", "Nastro compatto serale per To0670"],

    # PINEROLO & VALLI
    ["PINEROLO", "Pinerolo Centro Studi", "08:10", "Ba3520", "Ba3520 (Prosegue)", "Bus di Linea", "Corsa scolastica -> Sosta di legge -> Rientro linea 000280"],
    ["BARGE", "Pinerolo Stazione FS", "08:45", "Ba3510", "Ba3510 (Prosegue)", "Bus di Linea 000280", "Rientro in linea passeggeri a Barge alle 09:15"],
    ["PEROSA", "Pinerolo Movicentro", "09:15", "Pe0020", "Pe0040", "Bus di Linea", "Coincidenza studenti/operai Val Chisone"],
    ["PEROSA", "Perosa Deposito", "14:15", "Pe0070", "Pe0080", "Passaggio Bus sul Posto", "Cambio servizio pomeridiano Fenestrelle/Sestriere"],
    ["LUSERNA", "Pinerolo Movicentro", "13:45", "Lu0020", "Lu0050", "Bus di Linea", "Coincidenza linea Val Pellice / Torre Pellice"],
    ["PINEROLO", "Pinerolo Deposito", "14:35", "Pi0140", "Pi0140 (Pilota 40h)", "Proprio Bus Assegnato", "Turno 40h Lun-Ven continuativo (Sab+Dom libero)"],
    ["PINEROLO", "Pinerolo Deposito", "15:10", "Pi0200", "Pi0200 (Pilota 40h)", "Proprio Bus Assegnato", "Turno 40h Lun-Ven continuativo (Sab+Dom libero)"],

    # VALLE DI SUSA
    ["SUSA", "Susa Deposito", "12:30", "Su0010", "Su0060", "Passaggio Bus in Rimessa", "Rotazione linea Susa-Torino / Bussoleno"],
    ["SUSA", "Bussoleno FS", "14:10", "Su0020", "Su0040", "Coincidenza Bus", "Coincidenza treno SFM3 e scuole medie/superiori"],
    ["SALBERTRAND", "Oulx FS", "13:20", "Sa0010", "Sa0030", "Staffetta Mezzo", "Sanato superamento nastro 12h55 su Sa0030"],
    ["SALBERTRAND", "Bardonecchia FS", "17:45", "Sa0020", "Sa0060", "Passaggio Bus", "Copertura navetta alta valle / Frejus"],

    # VALLE D'AOSTA
    ["PONT ST. MARTIN", "Aosta Autostazione", "12:10", "Pt0611", "Pt0611 (Prosegue)", "Bus di Linea", "Eliminati 75 min di attesa passiva -> Rientro continuo a Pont"],
    ["IVREA", "Ivrea Movicentro", "14:00", "Iv0010", "Iv0030", "Passaggio Bus", "Coincidenza linea Ivrea-Torino e scuole del Canavese"]
]

ws.update(range_name=f'A1:G{len(dati_cambi_completi)}', values=dati_cambi_completi)
print("✅ FOGLIO 'CONFRONTO_CAMBI_TURNO' AGGIORNATO CON TUTTI I DEPOSITI SU GOOGLE SHEETS!")
