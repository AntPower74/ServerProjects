# ==============================================================================
# ⚙️ REGOLAMENTO E PARAMETRI CONFIGURABILI - CALCOLO TURNI & PROPOSTE (2025-2026)
# ==============================================================================
# Questo file è la "Sorgente di Verità" (Source of Truth) per tutti i calcoli, 
# la generazione dei PDF, l'audit dei turni e i dossier sindacali.
#
# Puoi modificare liberamente i valori, attivare/disattivare regole o aggiungere
# nuovi nodi di cambio e depositi. Ogni volta che modifichi questo file, gli script
# applicheranno automaticamente i nuovi parametri.
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. ⚖️ LIMITI CONTRATTUALI E NORMATIVI (CCNL & L. 138/1958)
# ------------------------------------------------------------------------------
LIMITI_NORMATIVI = {
    # Limite massimo inderogabile del nastro giornaliero (in ore decimali, es. 12.0 = 12h00)
    "NASTRO_MAX_LEGALE_ORE": 12.0,
    
    # Nastro target ideale per i turni compatti ristrutturati (es. 8.5 = 8h30)
    "NASTRO_TARGET_PROPOSTA_ORE": 8.5,
    
    # Retribuzione minima giornaliera per turno full-time (Garanzia CCNL in ore, 6.5 = 6h30)
    "PAGA_MINIMA_GIORNALIERA_ORE": 6.5,
    
    # Durata massima di guida continua consecutiva consentita prima di una sosta
    "GUIDA_CONTINUA_MAX_ORE": 5.0,
    
    # Soglia ore di lavoro continuativo per far scattare la pausa obbligatoria di 30m
    "SOGLIA_ORE_LAVORO_PER_PAUSA_30M": 6.0,
    
    # Minuti minimi di una sosta intermedia per azzerare il conteggio delle 6 ore consecutive
    "MINUTI_MINIMI_SOSTA_INTERMEDIA": 15,
    
    # Ore minime di riposo continuativo giornaliero tra due turni
    "RIPOSO_GIORNALIERO_MINIMO_ORE": 11.0,
    
    # Riposo continuativo standard nel proprio deposito di residenza
    "RIPOSO_DEPOSITO_RESIDENZA_ORE": 15.0
}

# ------------------------------------------------------------------------------
# 2. ⏱️ REGOLA DI CALCOLO DELLE RIPRESE (ACCORDO INTEGRATIVO AITO)
# ------------------------------------------------------------------------------
REGOLA_RIPRESE = {
    # La prima ripresa è sempre conteggiata all'inizio del servizio (presa servizio)
    "PRIMA_RIPRESA_A_INIZIO_TURNO": True,
    
    # Una sosta passiva genera una nuova ripresa (2ª, 3ª...) SOLO se supera questi minuti:
    "MINUTI_SOSTA_PER_SCATTO_RIPRESA": 30,
    
    # Se la sosta tra le corse è <= 30 minuti, il turno è considerato CONTINUO (1 ripresa)
    "SOSTA_MINORE_UGUALE_30M_E_CONTINUO": True
}

# ------------------------------------------------------------------------------
# 3. 🌟 TURNI SPECIALI A 40 ORE SETTIMANALI (SCHEMA 5+2: LUN-VEN)
# ------------------------------------------------------------------------------
# Inserisci o togli qui i codici dei turni da configurare a 40h (8h00 / giorno)
# con diritto al riposo fisso Sabato e Domenica:
TURNI_SPECIALI_40H = [
    "To0660",  # Torino Grugliasco (Servizio industriale e cambio Porta Susa)
    "Pi0140",  # Pinerolo Deposito
    "Pi0200",  # Pinerolo Deposito
    # "To0280", # Decommenta per impostare To0280 a 8h00 piene (attualmente compatto a 7h35)
]

PARAMETRI_40H = {
    "ORE_GIORNALIERE_40H": 8.0,       # 8h00 al giorno
    "GIORNI_LAVORATIVI": "Lun-Ven",
    "RIPOSO_SETTIMANALE": "Sabato e Domenica fissi (5+2)"
}

# ------------------------------------------------------------------------------
# 4. 📍 NODI DI INTERSCAMBIO E CAMBI SUL POSTO (CARLO FELICE & PORTA SUSA)
# ------------------------------------------------------------------------------
# Configurazione dei cambi con mezzo utilizzato (BUS o AUTO AZIENDALE)
MAPPA_CAMBI_TURNO = {
    # --- PIAZZA CARLO FELICE (Torino Porta Nuova - Navetta Caselle) ---
    "To0270": {
        "luogo": "piazza Carlo Felice",
        "ora_cambio": "11:00",
        "azione": "CEDE IL BUS",
        "turno_abbinato": "To0310",
        "mezzo_rientro": "AUTO AZIENDALE"
    },
    "To0310": {
        "luogo": "piazza Carlo Felice",
        "ora_cambio": "11:00",
        "azione": "RICEVE IL BUS",
        "turno_abbinato": "To0270",
        "mezzo_andata": "AUTO AZIENDALE"
    },
    "To0280": {
        "luogo": "piazza Carlo Felice",
        "ora_cambio": "11:45",
        "azione": "CEDE IL BUS",
        "turno_abbinato": "To0710",
        "mezzo_rientro": "AUTO AZIENDALE"
    },
    "To0710": {
        "luogo": "piazza Carlo Felice",
        "ora_cambio": "11:45",
        "azione": "RICEVE IL BUS",
        "turno_abbinato": "To0280",
        "mezzo_andata": "AUTO AZIENDALE"
    },
    "To0290": {
        "luogo": "piazza Carlo Felice",
        "ora_cambio": "12:15",
        "azione": "CEDE IL BUS",
        "turno_abbinato": "To0320",
        "mezzo_rientro": "AUTO AZIENDALE"
    },
    "To0320": {
        "luogo": "piazza Carlo Felice",
        "ora_cambio": "12:15",
        "azione": "RICEVE IL BUS",
        "turno_abbinato": "To0290",
        "mezzo_andata": "AUTO AZIENDALE"
    },
    "To0295": {
        "luogo": "piazza Carlo Felice",
        "ora_cambio": "12:45",
        "azione": "CEDE IL BUS",
        "turno_abbinato": "To0330",
        "mezzo_rientro": "AUTO AZIENDALE"
    },
    "To0330": {
        "luogo": "piazza Carlo Felice",
        "ora_cambio": "12:45",
        "azione": "RICEVE IL BUS",
        "turno_abbinato": "To0295",
        "mezzo_andata": "AUTO AZIENDALE"
    },
    "To0360": {
        "luogo": "piazza Carlo Felice",
        "ora_cambio": "18:15",
        "azione": "RICEVE IL BUS",
        "turno_abbinato": "To0320",
        "mezzo_andata": "AUTO AZIENDALE",
        "mezzo_rientro": "BUS (Corsa passeggeri 00:00 -> 00:45 da Caselle e poi rientro a Grugliasco)"
    },

    # --- CORSO BOLZANO (Torino Porta Susa - Auto di Servizio) ---
    "To0610": {
        "luogo": "Porta Susa (c.so Bolzano)",
        "ora_cambio": "09:30",
        "azione": "CEDE IL BUS",
        "turno_abbinato": "To0650",
        "mezzo_rientro": "AUTO AZIENDALE"
    },
    "To0650": {
        "luogo": "Porta Susa (c.so Bolzano)",
        "ora_cambio": "09:30",
        "azione": "RICEVE IL BUS",
        "turno_abbinato": "To0610",
        "mezzo_andata": "AUTO AZIENDALE"
    },
    "To0620": {
        "luogo": "Porta Susa (c.so Bolzano)",
        "ora_cambio": "09:30",
        "azione": "CEDE IL BUS",
        "turno_abbinato": "To0660",
        "mezzo_rientro": "AUTO AZIENDALE"
    },
    "To0660": {
        "luogo": "Porta Susa (c.so Bolzano)",
        "ora_cambio": "09:30",
        "azione": "RICEVE IL BUS",
        "turno_abbinato": "To0620",
        "mezzo_andata": "AUTO AZIENDALE"
    },
    "To0700": {
        "luogo": "Porta Susa (c.so Bolzano)",
        "ora_cambio": "12:45",
        "azione": "CEDE IL BUS",
        "turno_abbinato": "To0670",
        "mezzo_rientro": "AUTO AZIENDALE"
    },
    "To0670": {
        "luogo": "Porta Susa (c.so Bolzano)",
        "ora_cambio": "12:45",
        "azione": "RICEVE IL BUS",
        "turno_abbinato": "To0700",
        "mezzo_andata": "AUTO AZIENDALE"
    }
}

# ------------------------------------------------------------------------------
# 5. 🏢 REGOLAMENTO SPECIFICO PER DEPOSITO / RESIDENZA
# ------------------------------------------------------------------------------
REGOLE_DEPOSITI = {
    "SUSA": {
        "tipo": "Deposito Principale (Officina)",
        "residenza_obbligatoria": True,
        "separato_da_salbertrand": True
    },
    "SALBERTRAND": {
        "tipo": "Rimessa Distaccata",
        "residenza_obbligatoria": True,
        "separato_da_susa": True
    },
    "PIOBESI": {
        "tipo": "Deposito Dedicato (10 turni)",
        "stazione_rifornimento": "Beinasco CNG (Metano / Gasolio a fine corsa passeggeri)",
        "divieto_vuoti_rientro_piobesi": True
    },
    "BARGE": {
        "tipo": "Rimessa / Parcheggio",
        "rientro_linea_mattino": "Corsa 000280 delle 08:45 da Pinerolo FS a Barge (Arr. 09:15)"
    }
}
