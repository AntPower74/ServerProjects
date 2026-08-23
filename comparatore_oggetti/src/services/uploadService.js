export async function caricaFoto(file) {
  const formData = new FormData()
  formData.append('foto', file)

  const risposta = await fetch('/api/upload-foto', { method: 'POST', body: formData })
  if (!risposta.ok) {
    if (risposta.status === 413) {
      throw new Error('La foto è troppo grande. Prova a scattarne una con risoluzione più bassa, o scegli "Comprimi" se il telefono lo propone.')
    }
    const dati = await risposta.json().catch(() => ({}))
    throw new Error(dati.errore ?? 'Errore durante il caricamento della foto')
  }
  const dati = await risposta.json()
  return dati.url
}

// Apre subito una scheda vuota, da chiamare in modo sincrono dentro il gestore
// dell'evento utente (es. onChange dell'input file): i browser mobili bloccano
// window.open se arriva dopo un'attesa asincrona (come l'upload della foto).
export function apriFinestraVuota() {
  return window.open('about:blank', '_blank')
}

// Se una finestra è già aperta (vedi sopra) la reindirizza, altrimenti prova
// ad aprirne una nuova (funziona quando la chiamata parte da un click diretto).
export function apriGoogleLens(urlImmagine, finestra) {
  const urlLens = `https://lens.google.com/uploadbyurl?url=${encodeURIComponent(urlImmagine)}`
  if (finestra && !finestra.closed) {
    finestra.location.href = urlLens
  } else {
    window.open(urlLens, '_blank', 'noopener,noreferrer')
  }
}
