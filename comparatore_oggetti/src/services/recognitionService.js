// Riconoscimento immagine gratuito, interamente nel browser (nessuna chiamata
// server, nessuna chiave API, nessun costo). Usa MobileNet via TensorFlow.js:
// riconosce categorie generiche (es. "power drill", "backpack"), non marche o
// modelli specifici — per quello serve l'occhio umano via Google Lens.
let modelloPromise = null

function caricaModello() {
  if (!modelloPromise) {
    modelloPromise = Promise.all([
      import('@tensorflow/tfjs'),
      import('@tensorflow-models/mobilenet')
    ]).then(([, mobilenet]) => mobilenet.load())
  }
  return modelloPromise
}

function ripulisciEtichetta(etichetta) {
  // Le etichette MobileNet sono in inglese, tipo "backpack, back pack" o
  // "power drill". Prendiamo la prima variante e la rendiamo leggibile.
  const prima = etichetta.split(',')[0].trim()
  return prima.charAt(0).toUpperCase() + prima.slice(1)
}

export async function riconosciCategoriaGenerica(elementoImmagine) {
  const modello = await caricaModello()
  const predizioni = await modello.classify(elementoImmagine)
  if (!predizioni.length) return null

  const migliore = predizioni[0]
  return {
    etichetta: ripulisciEtichetta(migliore.className),
    confidenza: migliore.probability
  }
}
