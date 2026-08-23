function mediana(numeri) {
  if (numeri.length === 0) return null
  const ordinati = [...numeri].sort((a, b) => a - b)
  const meta = Math.floor(ordinati.length / 2)
  return ordinati.length % 2 !== 0
    ? ordinati[meta]
    : (ordinati[meta - 1] + ordinati[meta]) / 2
}

// Scarta i prezzi troppo lontani dalla mediana (outlier) prima di calcolare le statistiche finali.
function scartaOutlier(numeri, medianaBase) {
  if (medianaBase === null) return numeri
  return numeri.filter((p) => p >= medianaBase * 0.4 && p <= medianaBase * 2.2)
}

export function calcolaStatistiche(annunci, prezzoAcquisto = null, ricaricoPercentuale = 30) {
  const haPrezzo = prezzoAcquisto !== null && prezzoAcquisto !== undefined && prezzoAcquisto > 0
  const venduti = annunci.filter((a) => a.stato === 'venduto')
  const attivi = annunci.filter((a) => a.stato === 'attivo')

  const prezziVenduti = venduti.map((a) => a.prezzo)
  const prezziAttivi = attivi.map((a) => a.prezzo)
  const tuttiIPrezzi = annunci.map((a) => a.prezzo)

  const medianaGrezza = mediana(tuttiIPrezzi)
  const prezziPuliti = scartaOutlier(tuttiIPrezzi, medianaGrezza)

  const prezzoMedioVendita = venduti.length > 0
    ? mediana(scartaOutlier(prezziVenduti, mediana(prezziVenduti)))
    : mediana(prezziPuliti)

  // Vendibilità: rapporto tra annunci venduti recenti (domanda) e annunci
  // attivi (offerta). Più alto = si vende più facilmente rispetto a quanti
  // concorrenti stanno cercando di vendere la stessa cosa.
  const vendutiRecenti = venduti.filter((a) => a.giorniFa <= 30).length
  const sellThroughRate = annunci.length > 0
    ? venduti.length / annunci.length
    : 0

  let livelloVendibilita = 'bassa'
  if (sellThroughRate >= 0.5 || vendutiRecenti >= 3) livelloVendibilita = 'alta'
  else if (sellThroughRate >= 0.25 || vendutiRecenti >= 1) livelloVendibilita = 'media'

  const prezzoVenditaConsigliato = haPrezzo ? prezzoAcquisto * (1 + ricaricoPercentuale / 100) : null
  const margineDisponibile = haPrezzo && prezzoMedioVendita !== null
    ? prezzoMedioVendita - prezzoAcquisto
    : null
  const percentualeMargineReale = margineDisponibile !== null && haPrezzo
    ? (margineDisponibile / prezzoAcquisto) * 100
    : null

  const convieneComprare = percentualeMargineReale !== null && percentualeMargineReale >= ricaricoPercentuale

  return {
    numeroAnnunci: annunci.length,
    numeroVenduti: venduti.length,
    numeroAttivi: attivi.length,
    prezzoMinimo: prezziPuliti.length ? Math.min(...prezziPuliti) : null,
    prezzoMassimo: prezziPuliti.length ? Math.max(...prezziPuliti) : null,
    prezzoMedioVendita,
    prezzoMedioAttivi: mediana(prezziAttivi),
    sellThroughRate,
    livelloVendibilita,
    prezzoVenditaConsigliato,
    margineDisponibile,
    percentualeMargineReale,
    convieneComprare
  }
}
