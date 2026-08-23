import 'dotenv/config'
import express from 'express'
import cors from 'cors'
import multer from 'multer'
import crypto from 'crypto'
import { cercaSuTutteLePiattaforme } from './searchAggregator.js'
import { valutaOggettoUniversale } from './aiEvaluator.js'
import db from './db.js'
import { avviaMonitoraggio } from './monitor.js'
import { pushAbilitato } from './webpush.js'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const app = express()
app.set('trust proxy', true)
app.use(cors())

const cartellaUpload = path.join(__dirname, 'uploads')
const upload = multer({
  storage: multer.diskStorage({
    destination: cartellaUpload,
    filename: (req, file, cb) => {
      const estensione = path.extname(file.originalname) || '.jpg'
      cb(null, `${crypto.randomUUID()}${estensione}`)
    }
  }),
  limits: { fileSize: 15 * 1024 * 1024 },
  fileFilter: (req, file, cb) => cb(null, file.mimetype.startsWith('image/'))
})
app.use('/uploads', express.static(cartellaUpload))

// Carica una foto e restituisce l'URL pubblico, per passarla a Google Lens (gratuito)
app.post('/api/upload-foto', upload.single('foto'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ errore: 'Nessuna immagine ricevuta' })
  }
  const url = `${req.protocol}://${req.get('host')}/uploads/${req.file.filename}`
  res.status(201).json({ url })
})

// Endpoint generico di ricerca multipiattaforma
app.get('/api/search', async (req, res) => {
  const query = req.query.q
  if (!query) {
    return res.status(400).json({ errore: 'Parametro "q" mancante' })
  }

  try {
    const annunciCombinati = await cercaSuTutteLePiattaforme(query)
    res.json({ annunci: annunciCombinati })
  } catch (errore) {
    console.error("Errore fatale:", errore)
    res.status(500).json({ errore: 'Errore interno del server' })
  }
})

// Endpoint di Valutazione Universale per Flipping (qualsiasi categoria di oggetto)
app.post('/api/ai-evaluate', express.json(), (req, res) => {
  const { text } = req.body
  if (!text || !text.trim()) {
    return res.status(400).json({ errore: 'Testo annuncio mancante' })
  }
  const valutazione = valutaOggettoUniversale(text)
  res.json({ valutazione })
})

// === NUOVI ENDPOINT PER IL DATABASE ===

// Salva una nuova ricerca da monitorare
app.post('/api/salva-ricerca', express.json(), (req, res) => {
  const { nome_oggetto, prezzo_bersaglio } = req.body;
  if (!nome_oggetto || !prezzo_bersaglio) {
    return res.status(400).json({ errore: 'Dati mancanti' });
  }

  db.run(
    `INSERT INTO ricerche_salvate (nome_oggetto, prezzo_bersaglio) VALUES (?, ?)`,
    [nome_oggetto, prezzo_bersaglio],
    function(err) {
      if (err) return res.status(500).json({ errore: err.message });
      res.status(201).json({ id: this.lastID, messaggio: 'Ricerca salvata e monitoraggio attivato' });
    }
  );
});

// Ottiene tutte le ricerche salvate
app.get('/api/ricerche-salvate', (req, res) => {
  db.all(`SELECT * FROM ricerche_salvate ORDER BY data_salvataggio DESC`, (err, rows) => {
    if (err) return res.status(500).json({ errore: err.message });
    res.json({ ricerche: rows });
  });
});

// Elimina una ricerca monitorata
app.delete('/api/ricerche-salvate/:id', (req, res) => {
  db.run(`DELETE FROM ricerche_salvate WHERE id = ?`, [req.params.id], function(err) {
    if (err) return res.status(500).json({ errore: err.message });
    if (this.changes === 0) return res.status(404).json({ errore: 'Ricerca non trovata' });
    res.json({ messaggio: 'Ricerca eliminata' });
  });
});

// === NOTIFICHE PUSH ===

// Chiave pubblica VAPID per la sottoscrizione lato client
app.get('/api/push/public-key', (req, res) => {
  if (!pushAbilitato) {
    return res.status(503).json({ errore: 'Notifiche push non configurate sul server' });
  }
  res.json({ chiavePubblica: process.env.VAPID_PUBLIC_KEY });
});

// Registra una sottoscrizione push del browser
app.post('/api/push/subscribe', express.json(), (req, res) => {
  const subscription = req.body;
  if (!subscription?.endpoint) {
    return res.status(400).json({ errore: 'Sottoscrizione non valida' });
  }

  db.run(
    `INSERT OR REPLACE INTO push_subscriptions (endpoint, subscription_json) VALUES (?, ?)`,
    [subscription.endpoint, JSON.stringify(subscription)],
    function(err) {
      if (err) return res.status(500).json({ errore: err.message });
      res.status(201).json({ messaggio: 'Notifiche push attivate' });
    }
  );
});

// Rimuove una sottoscrizione push
app.post('/api/push/unsubscribe', express.json(), (req, res) => {
  const { endpoint } = req.body;
  if (!endpoint) {
    return res.status(400).json({ errore: 'Endpoint mancante' });
  }
  db.run(`DELETE FROM push_subscriptions WHERE endpoint = ?`, [endpoint], (err) => {
    if (err) return res.status(500).json({ errore: err.message });
    res.json({ messaggio: 'Notifiche push disattivate' });
  });
});

// Avvia il sistema di monitoraggio in background
avviaMonitoraggio();

// Serve il frontend statico (React/Vite build)
app.use(express.static(path.join(__dirname, '../dist'), {
  setHeaders: (res, pathUrl) => {
    if (pathUrl.endsWith('.html') || pathUrl.endsWith('sw.js')) {
      res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate')
    }
  }
}))

// Qualsiasi altra rotta non-API viene servita da React Router (se presente) o dalla index
app.get('*', (req, res) => {
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate')
  res.sendFile(path.join(__dirname, '../dist/index.html'))
})

// Gestione errori di multer (es. foto oltre il limite di 15MB): senza questo
// Express risponderebbe con una pagina di errore HTML invece che JSON, e il
// frontend non riuscirebbe a leggere il messaggio (dati.json() fallirebbe).
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE') {
      return res.status(413).json({ errore: 'File troppo grande (limite 15MB).' })
    }
    return res.status(400).json({ errore: err.message })
  }
  next(err)
})

const PORTA = process.env.PORT || 3001
app.listen(PORTA, () => {
  console.log(`Backend eBay in ascolto su http://localhost:${PORTA}`)
})
