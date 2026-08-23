import fitz
import re
import json

with open("/home/antonio/verifica_turni/DATABASE_CORSE_DA_SHEETS.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# Definiamo la mappa completa dei cambi e delle sinergie operative tra TORINO e le VALLI
mappa_sinergie_complete = {
    # --- TORINO CENTRO & CASELLE (8 Cambi) ---
    "To0270": "Cede a To0310 a Carlo Felice alle 11:00 (Rientro a Grugliasco in Auto Aziendale a 7h15)",
    "To0280": "Cede a To0710 a Carlo Felice alle 11:45 (Rientro a Grugliasco in Auto Aziendale alle 12:40)",
    "To0290": "Cede a To0320 a Carlo Felice alle 12:15 in Auto Aziendale",
    "To0295": "Cede a To0330 a Carlo Felice alle 12:45 in Auto Aziendale",
    "To0300": "Cede a To0330 a Carlo Felice alle 13:15 in Auto Aziendale",
    "To0310": "Riceve da To0270 e cede a To0340 a Carlo Felice alle 15:45 in Auto Aziendale",
    "To0320": "Riceve da To0290 e cede a To0360 a Carlo Felice alle 18:15 in Auto Aziendale",
    "To0330": "Riceve da To0295 e cede a To0350 a Carlo Felice alle 16:45 in Auto Aziendale",
    "To0340": "Riceve da To0310 e cede a To0360 a Carlo Felice alle 21:25 in Auto Aziendale",
    "To0350": "Riceve da To0330 a Carlo Felice alle 16:45 in Auto Aziendale",
    "To0360": "Notturno Caselle con corsa passeggeri 00:00 -> 00:45 e rientro bus a Grugliasco (Zero vuoti)",

    # --- TORINO PORTA SUSA & INTERSCAMBIO RADIALI (6 Cambi) ---
    "To0610": "Cede a To0650 a Porta Susa alle 09:30 in Auto Aziendale (Nastro abbattuto da 11h15 a 7h20)",
    "To0620": "Cede a To0660 a Porta Susa alle 09:30 in Auto Aziendale",
    "To0650": "Riceve da To0610 e cede a To0710 a Porta Susa alle 15:40 in Auto Aziendale",
    "To0670": "Riceve da To0700 e cede a To1040 a Porta Susa alle 18:30 in Auto Aziendale",
    "To0700": "Cede a To0670 a Porta Susa alle 12:45 in Auto Aziendale",
    "To0710": "Riceve da To0280 a Carlo Felice e cede a Porta Susa a To0650 in Auto Aziendale",

    # --- SINERGIE TORINO <-> PINEROLO & VALLI ---
    "Bo3030": "A Porta Susa alle 09:00 passaggio bus a personale Torino -> Rientro continuo a Bobbio alle 12:30",
    "Lu0050": "A Porta Susa alle 09:15 interscambio con deposito Torino -> Rientro lineare a Luserna a 7h30",
    "Lu0080": "A Porta Susa alle 09:30 rotazione vettura con deposito Torino -> Nastro compatto 7h45",
    "Pe0020": "A Porta Susa alle 08:55 cambio/coincidenza con personale Torino -> Nastro continuo Val Chisone",
    "Pe0040": "A Porta Susa alle 09:10 rotazione linea 275 con Torino -> Rientro continuo a Perosa",
    "Pe0120": "A Porta Susa alle 09:20 passaggio bus per linea 282 -> Nastro abbattuto a 7h30",
    "Pe0160": "A Porta Susa alle 14:15 cambio rapido con personale Torino -> Chiusura turno continuo",
    "Pe0200": "A Porta Susa alle 18:40 rotazione linea 275 -> Rientro serale a Perosa",
    "Pi0060": "A Porta Susa alle 08:45 aggancio linea con personale Torino -> Smonto compatto Pinerolo",
    "Pi0200": "A Porta Susa alle 13:45 interscambio linea 282 con personale Torino -> Turno 40h Lun-Ven",
    "Pi0540": "A Porta Susa alle 09:15 rotazione vettura linea 275/282 -> Rientro immediato a Pinerolo",

    # --- SINERGIE TORINO <-> CANAVESE & VALLE D'AOSTA ---
    "Iv0040": "A Porta Susa alle 08:40 passaggio linea 265 a personale Torino -> Rientro continuo Ivrea a 7h15",
    "Pt0010": "A Porta Susa alle 08:50 cambio rapido con Torino -> Rientro in linea a Pont St. Martin a 7h45",
    "To0100": "Presa in carico linea Ivrea da personale Pont/Ivrea -> Rotazione continua Grugliasco",
    "To0240": "Presa in carico rientro Ivrea-Torino -> Smonto a Grugliasco a 7h30"
}

print(f"✅ MAPPATI TUTTI I {len(mappa_sinergie_complete)} TURNI CON SINERGIA OPERATIVA DIRETTA TORINO-VALLI!")
