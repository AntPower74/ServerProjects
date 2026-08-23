import sqlite3 from 'sqlite3'
import fs from 'fs'

// Crea la cartella dati se non esiste
const dbDir = './data'
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir)
}

// Inizializza il database
const db = new sqlite3.Database('./data/comparatore.db')

// Crea la tabella al primo avvio
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS ricerche_salvate (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nome_oggetto TEXT NOT NULL,
      prezzo_bersaglio REAL NOT NULL,
      data_salvataggio DATETIME DEFAULT CURRENT_TIMESTAMP,
      ultimo_controllo DATETIME,
      prezzo_corrente REAL,
      notifica_inviata INTEGER DEFAULT 0
    )
  `)

  db.run(`
    CREATE TABLE IF NOT EXISTS push_subscriptions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      endpoint TEXT NOT NULL UNIQUE,
      subscription_json TEXT NOT NULL,
      data_creazione DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `)

  // Migrazione: aggiunge la colonna a chi ha già un DB da prima delle notifiche push
  db.run(`ALTER TABLE ricerche_salvate ADD COLUMN notifica_inviata INTEGER DEFAULT 0`, () => {})
})

export default db
