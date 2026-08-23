import cron from 'node-cron'
import db from './db.js'
import webpush, { pushAbilitato } from './webpush.js'
import { cercaSuTutteLePiattaforme } from './searchAggregator.js'

function prezzoMinimo(annunci) {
  let minimo = null
  for (const annuncio of annunci) {
    const prezzo = parseFloat(String(annuncio.prezzo).replace(',', '.'))
    if (!isNaN(prezzo) && (minimo === null || prezzo < minimo)) {
      minimo = prezzo
    }
  }
  return minimo
}

function inviaNotificaPush(ricerca, prezzoTrovato) {
  if (!pushAbilitato) return

  db.all(`SELECT * FROM push_subscriptions`, (err, subs) => {
    if (err || subs.length === 0) return

    const payload = JSON.stringify({
      title: 'Prezzo sceso! 🛎️',
      body: `"${ricerca.nome_oggetto}" ora costa €${prezzoTrovato} (target: €${ricerca.prezzo_bersaglio})`,
      url: '/'
    })

    subs.forEach(sub => {
      const subscription = JSON.parse(sub.subscription_json)
      webpush.sendNotification(subscription, payload).catch(errore => {
        // Sottoscrizione scaduta o revocata: la rimuoviamo
        if (errore.statusCode === 404 || errore.statusCode === 410) {
          db.run(`DELETE FROM push_subscriptions WHERE id = ?`, [sub.id])
        } else {
          console.error('Errore invio push:', errore.message)
        }
      })
    })
  })
}

export function avviaMonitoraggio() {
  console.log("Sorvegliante prezzi (Cron Job) inizializzato.");

  // In produzione un controllo ogni 6 ore è più che sufficiente ('0 */6 * * *')
  cron.schedule('* * * * *', () => {
    db.all(`SELECT * FROM ricerche_salvate`, async (err, rows) => {
      if (err) {
        console.error("Errore lettura DB monitor:", err.message);
        return;
      }

      if (rows.length === 0) return;

      for (const ricerca of rows) {
        try {
          const annunci = await cercaSuTutteLePiattaforme(ricerca.nome_oggetto)
          const migliorPrezzo = prezzoMinimo(annunci)

          if (migliorPrezzo === null) continue

          const target = parseFloat(ricerca.prezzo_bersaglio)
          const calato = migliorPrezzo <= target

          db.run(
            `UPDATE ricerche_salvate SET ultimo_controllo = CURRENT_TIMESTAMP, prezzo_corrente = ? WHERE id = ?`,
            [migliorPrezzo, ricerca.id]
          );

          if (calato && !ricerca.notifica_inviata) {
            console.log(`🛎️ [NOTIFICA]: "${ricerca.nome_oggetto}" è sceso a €${migliorPrezzo}`);
            inviaNotificaPush(ricerca, migliorPrezzo)
            db.run(`UPDATE ricerche_salvate SET notifica_inviata = 1 WHERE id = ?`, [ricerca.id])
          } else if (!calato && ricerca.notifica_inviata) {
            // Il prezzo è risalito sopra il target: permettiamo una nuova notifica al prossimo calo
            db.run(`UPDATE ricerche_salvate SET notifica_inviata = 0 WHERE id = ?`, [ricerca.id])
          }
        } catch (erroreRicerca) {
          console.error(`Errore monitoraggio "${ricerca.nome_oggetto}":`, erroreRicerca.message);
        }
      }
    });
  });
}
