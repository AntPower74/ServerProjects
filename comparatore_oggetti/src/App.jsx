import { useEffect, useRef, useState } from 'react'
import { Camera, Images, Loader2, RotateCcw, Search, BookmarkCheck, ExternalLink, X, Sparkles, ClipboardPaste, Zap, Target } from 'lucide-react'
import { caricaFoto, apriGoogleLens, apriFinestraVuota } from './services/uploadService.js'
import { riconosciCategoriaGenerica } from './services/recognitionService.js'
import { cercaAnnunciSimili } from './services/market.js'
import { SITI_MERCATO, apriSitoMercato } from './services/ricercaSiti.js'
import { calcolaStatistiche } from './utils/pricing.js'
import { estraiPrezziDaTesto } from './utils/estraiPrezzi.js'
import { estraiRisultatiDaHtml } from './utils/estraiRisultatiLens.js'
import RisultatiPanel from './components/RisultatiPanel.jsx'
import ArchivioRicerche from './components/ArchivioRicerche.jsx'
import FlipRadarHub from './components/FlipRadarHub.jsx'
import RadarOfferteView from './components/RadarOfferteView.jsx'

const FASI = {
  INPUT: 'input',
  RICERCA: 'ricerca',
  RISULTATI: 'risultati'
}

const OGGETTO_VUOTO = { marca: '', nome: '', categoria: '', condizione: '', descrizione: '' }

function caricaElementoImmagine(url) {
  return new Promise((resolve, reject) => {
    const img = new window.Image()
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = url
  })
}

export default function App() {
  const [fase, setFase] = useState(FASI.INPUT)
  const [anteprimaFoto, setAnteprimaFoto] = useState(null)
  const [fileFoto, setFileFoto] = useState(null)
  const [urlFotoCaricata, setUrlFotoCaricata] = useState(null)
  const [caricandoFoto, setCaricandoFoto] = useState(false)
  const [riconoscendoFoto, setRiconoscendoFoto] = useState(false)
  const [suggerimentoAI, setSuggerimentoAI] = useState(null)
  const [oggetto, setOggetto] = useState(OGGETTO_VUOTO)
  const [annunci, setAnnunci] = useState([])
  const [statistiche, setStatistiche] = useState(null)
  const [prezzoRichiesto, setPrezzoRichiesto] = useState(null)
  const [testoIncollato, setTestoIncollato] = useState('')
  const [mostraIncolla, setMostraIncolla] = useState(false)
  const [tabAttivo, setTabAttivo] = useState('radar')
  const [estensioneInstallata, setEstensioneInstallata] = useState(false)
  const inputFotoCameraRef = useRef(null)
  const inputFotoGalleriaRef = useRef(null)
  const flipHubRef = useRef(null)
  const tabAttivoRef = useRef(tabAttivo)
  useEffect(() => { tabAttivoRef.current = tabAttivo }, [tabAttivo])

  async function handleFotoSelezionata(file) {
    if (!file) return
    const url = URL.createObjectURL(file)
    setAnteprimaFoto(url)
    setFileFoto(file)
    setUrlFotoCaricata(null)
    setSuggerimentoAI(null)
    setRiconoscendoFoto(true)
    try {
      const elementoImmagine = await caricaElementoImmagine(url)
      const risultato = await riconosciCategoriaGenerica(elementoImmagine)
      if (risultato) {
        setSuggerimentoAI(risultato.etichetta)
        setOggetto((prev) => (prev.nome.trim() ? prev : { ...prev, nome: risultato.etichetta }))
      }
    } catch (e) {
      console.error('Riconoscimento sul dispositivo non riuscito:', e)
    } finally {
      setRiconoscendoFoto(false)
    }
  }

  // Segnala all'estensione "Estrai per Prezzly" (se installata) che stiamo per
  // aprire Google Lens: il suo content script su questa pagina intercetta il
  // messaggio e arma l'estrazione automatica sulla scheda di Lens che si apre.
  // Se l'estensione non è installata questo messaggio semplicemente non ha ascoltatori.
  function apriLensArmandoEstensione(url, finestra) {
    apriGoogleLens(url, finestra)
    window.postMessage({ type: 'prezzly:arma-estensione' }, window.location.origin)
  }

  // Se l'estensione è installata le chiediamo di cercare in background su
  // Subito/Vinted/Marketplace e consegnare i risultati da sola (nessuna
  // scheda visibile, nessun click): li riceviamo più avanti nello stesso
  // ascoltatore 'message' che gestisce Lens. Senza estensione questa
  // chiamata non ha ascoltatori e non fa nulla: restano i pulsanti manuali.
  function cercaSuSitiEsterni(query) {
    if (!estensioneInstallata) return
    window.postMessage({ type: 'prezzly:cerca-mercato', query, siti: Object.keys(SITI_MERCATO) }, window.location.origin)
  }

  // Pulsante manuale: carica la foto e apre Google Lens per un riconoscimento
  // più preciso (marca/modello, non solo categoria generica).
  async function handleApriLens() {
    if (!fileFoto) return
    setCaricandoFoto(true)
    // Apriamo la scheda subito, ancora dentro il gesto dell'utente: se aspettiamo
    // la fine dell'upload (asincrono) i browser mobili bloccano il popup.
    const finestraLens = apriFinestraVuota()
    try {
      const url = await caricaFoto(fileFoto)
      setUrlFotoCaricata(url)
      apriLensArmandoEstensione(url, finestraLens)
    } catch (e) {
      console.error(e)
      if (finestraLens && !finestraLens.closed) finestraLens.close()
      alert(e.message || 'Non sono riuscito a caricare la foto su Google Lens.')
    } finally {
      setCaricandoFoto(false)
    }
  }

  function rimuoviFoto() {
    setAnteprimaFoto(null)
    setFileFoto(null)
    setUrlFotoCaricata(null)
    setSuggerimentoAI(null)
    if (inputFotoCameraRef.current) inputFotoCameraRef.current.value = ''
    if (inputFotoGalleriaRef.current) inputFotoGalleriaRef.current.value = ''
  }

  // Se il testo è HTML (Copy outerHTML da DevTools, o quello che manda il
  // bookmarklet/estensione) estraiamo titolo/prezzo/fonte/link per ogni
  // prodotto. Se sappiamo già da quale sito viene (bookmarklet/estensione lo
  // dichiarano) usiamo solo quel parser; altrimenti (incolla manuale) proviamo
  // tutti i parser e uniamo quello che trovano. Se non troviamo nulla di
  // strutturato ripieghiamo sull'estrazione dei soli prezzi (testo semplice).
  function estraiAnnunciDaTesto(testo, sito) {
    const risultatiStrutturati = sito
      ? estraiRisultatiDaHtml(testo, sito)
      : Object.keys(SITI_MERCATO).concat('lens').flatMap((s) => estraiRisultatiDaHtml(testo, s))
    if (risultatiStrutturati.length > 0) return risultatiStrutturati

    const prezzi = estraiPrezziDaTesto(testo)
    if (prezzi.length === 0) return []
    return prezzi.map((prezzo, i) => ({
      id: `incollato-${i}`,
      prezzo,
      stato: 'attivo',
      sorgente: 'Incollato da Google',
      giorniFa: null
    }))
  }

  // Aggiunge nuovi annunci a quelli già presenti (non li sostituisce): eBay,
  // Lens, Subito, Vinted e Marketplace possono arrivare in momenti diversi
  // (l'estensione consegna i risultati dei marketplace in background, mentre
  // eBay/Lens sono già a schermo) e devono finire nella stessa lista unica.
  function applicaAnnunciEstratti(nuoviAnnunci) {
    setAnnunci((prev) => {
      const uniti = [...prev, ...nuoviAnnunci]
      setStatistiche(calcolaStatistiche(uniti, null))
      return uniti
    })
    setPrezzoRichiesto(null)
    setFase(FASI.RISULTATI)
  }

  function handleEstraiDaTesto(event) {
    event.preventDefault()
    if (!oggetto.nome.trim()) {
      alert("Scrivi prima il nome dell'oggetto qui sotto, poi estrai i prezzi.")
      return
    }
    const annunciEstratti = estraiAnnunciDaTesto(testoIncollato)
    if (annunciEstratti.length === 0) {
      alert('Non ho trovato prezzi. Incolla l\'HTML della pagina (Copy outerHTML da DevTools) oppure il testo con i prezzi in euro (es. "90 €").')
      return
    }
    applicaAnnunciEstratti(annunciEstratti)
  }

  // Riceve l'HTML dei risultati (Lens, Subito, Vinted, Marketplace) senza
  // copia-incolla manuale, in due modi:
  // 1) Bookmarklet "Estrai per Prezzly": la scheda del sito ci apre/riattiva con
  //    window.open(url, 'prezzlyTab') e ci manda {site, html} via postMessage
  //    (evento.source è quella scheda, cioè window.opener).
  // 2) Estensione: il suo content script gira nella NOSTRA scheda (isolated world) e
  //    ci passa l'HTML già estratto tramite postMessage nella stessa finestra
  //    (evento.source === window) — sia per Lens (scheda in primo piano che l'utente
  //    ha aperto) sia per Subito/Vinted/Marketplace (schede aperte ed estratte in
  //    background, mai viste dall'utente). Lo stesso canale ci dice anche se
  //    l'estensione è installata ('prezzly:estensione-presente').
  useEffect(() => {
    function gestisciHtmlEstratto(html, sito) {
      const annunciEstratti = estraiAnnunciDaTesto(html, sito)
      if (annunciEstratti.length === 0) return false

      // Se la ricerca in background è partita dalla scheda Flipping, i risultati
      // vanno uniti lì (il suo stato è interno al componente), non nella
      // "Ricerca Live" di questa pagina.
      if (tabAttivoRef.current === 'flipping' && flipHubRef.current) {
        flipHubRef.current.aggiungiAnnunciMercato(annunciEstratti)
        return true
      }

      setOggetto((prev) => {
        if (prev.nome.trim()) return prev
        const primoTitolo = annunciEstratti.find((a) => a.titolo)?.titolo
        return primoTitolo ? { ...prev, nome: primoTitolo.slice(0, 60) } : prev
      })
      applicaAnnunciEstratti(annunciEstratti)
      return true
    }

    // Il sito d'origine (Google/Subito/Vinted/Facebook) del messaggio, per
    // scartare qualunque cosa arrivi da un'altra origine.
    function sitoDaOrigine(origin) {
      let host
      try {
        host = new URL(origin).hostname
      } catch {
        return null
      }
      if (/(^|\.)google\.[a-z.]+$/i.test(host)) return 'lens'
      if (/(^|\.)subito\.it$/i.test(host)) return 'subito'
      if (/(^|\.)vinted\.[a-z.]+$/i.test(host)) return 'vinted'
      if (/(^|\.)facebook\.com$/i.test(host)) return 'marketplace'
      return null
    }

    function alMessaggio(evento) {
      if (evento.source === window && evento.origin === window.location.origin) {
        const dati = evento.data
        if (dati?.type === 'prezzly:estensione-html') {
          gestisciHtmlEstratto(dati.html, dati.site)
        } else if (dati?.type === 'prezzly:estensione-presente') {
          setEstensioneInstallata(true)
        }
        return
      }

      if (!window.opener || evento.source !== window.opener) return
      const sitoOrigine = sitoDaOrigine(evento.origin)
      if (!sitoOrigine) return

      const dati = evento.data
      let html, sito
      if (dati && typeof dati === 'object' && typeof dati.html === 'string') {
        html = dati.html
        sito = dati.site || sitoOrigine
      } else if (typeof dati === 'string' && dati.length >= 50 && dati.includes('<')) {
        // Retrocompat: vecchia versione del bookmarklet, mandava l'HTML nudo.
        html = dati
        sito = sitoOrigine
      } else {
        return
      }

      if (gestisciHtmlEstratto(html, sito)) {
        try {
          window.opener.postMessage('prezzly-ricevuto', evento.origin)
        } catch (e) {
          console.error(e)
        }
      }
    }

    // Ci diamo un nome fisso: senza estensione, il bookmarklet su Subito/Vinted/
    // Marketplace/Lens punta sempre a window.open(url, 'prezzlyTab') per tornare
    // alla scheda da cui l'utente è partito invece di aprirne una nuova vuota
    // (che perderebbe l'analisi/ricerca in corso). Funziona solo se questa è
    // già una scheda del browser normale aperta prima del bookmarklet — un'app
    // installata (PWA standalone) è isolata dalle schede del browser e questo
    // trucco non può raggiungerla, limite della piattaforma non aggirabile.
    window.name = 'prezzlyTab'

    window.addEventListener('message', alMessaggio)
    // Chiediamo all'estensione (se installata) di segnalarsi: decide se
    // mostrare i pulsanti manuali di fallback per Subito/Vinted/Marketplace.
    window.postMessage({ type: 'prezzly:controlla-estensione' }, window.location.origin)
    if (window.opener) {
      try {
        window.opener.postMessage('prezzly-pronto', '*')
      } catch (e) {
        console.error(e)
      }
    }

    return () => window.removeEventListener('message', alMessaggio)
  }, [])

  async function avviaRicercaMercato(event) {
    event.preventDefault()
    if (!oggetto.nome.trim()) return

    setFase(FASI.RICERCA)
    const queryDiRicerca = oggetto.marca ? `${oggetto.marca} ${oggetto.nome}` : oggetto.nome
    // Non aspettiamo Subito/Vinted/Marketplace per mostrare i primi risultati:
    // partono in parallelo (se l'estensione c'è) e si aggiungono da soli alla
    // lista quando arrivano, tramite lo stesso listener usato per Lens.
    cercaSuSitiEsterni(queryDiRicerca)
    const risultatiAnnunci = await cercaAnnunciSimili(queryDiRicerca)
    applicaAnnunciEstratti(risultatiAnnunci)
  }

  function calcolaMargine(prezzo) {
    const stats = calcolaStatistiche(annunci, prezzo)
    setStatistiche(stats)
    setPrezzoRichiesto(prezzo)
  }

  function ricomincia() {
    setFase(FASI.INPUT)
    rimuoviFoto()
    setOggetto(OGGETTO_VUOTO)
    setAnnunci([])
    setStatistiche(null)
    setPrezzoRichiesto(null)
    setTestoIncollato('')
    setMostraIncolla(false)
  }

  return (
    <div
      className="min-h-screen bg-slate-950 px-4 text-slate-100"
      style={{
        paddingTop: 'max(2rem, env(safe-area-inset-top))',
        paddingBottom: 'max(5rem, calc(env(safe-area-inset-bottom) + 2rem))'
      }}
    >
      <div className="mx-auto max-w-md">
        <header className="mb-8 flex flex-col gap-4 border-b border-slate-800/50 pb-5">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="flex items-baseline gap-2 text-3xl font-extrabold bg-gradient-to-r from-indigo-400 to-emerald-400 bg-clip-text text-transparent tracking-tight">
                Prezzly
                <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest border border-indigo-500/30 bg-indigo-500/10 px-1.5 py-0.5 rounded">Beta</span>
              </h1>
              <p className="text-xs font-medium text-slate-500 mt-1 tracking-wide">IL TUO COMPARATORE SMART</p>
            </div>
            {fase !== FASI.INPUT && tabAttivo === 'ricerca' && (
              <button
                onClick={ricomincia}
                className="rounded-full bg-slate-900 p-2.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
                aria-label="Nuova ricerca"
                title="Nuova ricerca"
              >
                <RotateCcw className="h-4 w-4" />
              </button>
            )}
          </div>

          <div className="flex bg-slate-900/60 p-1 rounded-xl gap-1">
            <button
              onClick={() => setTabAttivo('radar')}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1 ${
                tabAttivo === 'radar'
                ? 'bg-gradient-to-r from-indigo-600 to-emerald-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Target className="w-3.5 h-3.5 text-indigo-300" /> Radar Offerte
            </button>
            <button
              onClick={() => setTabAttivo('flipping')}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1 ${
                tabAttivo === 'flipping'
                ? 'bg-slate-800 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Zap className="w-3.5 h-3.5 text-amber-400" /> Flipping & OCR
            </button>
            <button
              onClick={() => setTabAttivo('ricerca')}
              className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                tabAttivo === 'ricerca'
                ? 'bg-slate-800 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Ricerca Live
            </button>
            <button
              onClick={() => setTabAttivo('archivio')}
              className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1 ${
                tabAttivo === 'archivio'
                ? 'bg-slate-800 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <BookmarkCheck className="w-3.5 h-3.5" /> Archivio
            </button>
          </div>
        </header>

        {tabAttivo === 'radar' ? (
          <RadarOfferteView
            estensioneInstallata={estensioneInstallata}
            onCercaSitiEsterni={cercaSuSitiEsterni}
          />
        ) : tabAttivo === 'flipping' ? (
          <FlipRadarHub
            ref={flipHubRef}
            estensioneInstallata={estensioneInstallata}
            onCercaSitiEsterni={cercaSuSitiEsterni}
            onSearchMarketplace={(query) => {
              setOggetto({ ...OGGETTO_VUOTO, nome: query })
              setTabAttivo('ricerca')
              setFase(FASI.INPUT)
            }}
          />
        ) : tabAttivo === 'archivio' ? (
          <ArchivioRicerche />
        ) : (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">

        {fase === FASI.INPUT && (
          <form onSubmit={avviaRicercaMercato} className="space-y-4">
            <p className="text-sm text-slate-400 mb-2">Cosa vuoi cercare?</p>

            {anteprimaFoto ? (
              <div className="relative overflow-hidden rounded-xl border border-slate-700">
                <img src={anteprimaFoto} alt="Foto oggetto" className="h-40 w-full object-cover" />
                <button
                  type="button"
                  onClick={rimuoviFoto}
                  className="absolute right-2 top-2 rounded-full bg-slate-950/80 p-1.5 text-slate-300 hover:text-white"
                  aria-label="Rimuovi foto"
                >
                  <X className="h-4 w-4" />
                </button>
                {riconoscendoFoto && (
                  <div className="absolute inset-0 flex items-center justify-center gap-2 bg-slate-950/70 text-sm text-slate-200">
                    <Loader2 className="h-4 w-4 animate-spin" /> Riconoscimento sul dispositivo...
                  </div>
                )}
                {caricandoFoto && (
                  <div className="absolute inset-0 flex items-center justify-center gap-2 bg-slate-950/70 text-sm text-slate-200">
                    <Loader2 className="h-4 w-4 animate-spin" /> Apertura Google Lens...
                  </div>
                )}
                {!riconoscendoFoto && !caricandoFoto && (
                  <button
                    type="button"
                    onClick={urlFotoCaricata ? () => apriLensArmandoEstensione(urlFotoCaricata) : handleApriLens}
                    className="absolute bottom-2 right-2 flex items-center gap-1.5 rounded-full bg-slate-950/80 px-3 py-1.5 text-xs font-medium text-slate-200 hover:text-white"
                  >
                    <ExternalLink className="h-3.5 w-3.5" /> {urlFotoCaricata ? 'Riapri Google Lens' : 'Apri Google Lens'}
                  </button>
                )}
              </div>
            ) : (
              <div className="flex gap-3">
                <label className="flex flex-1 cursor-pointer flex-col items-center gap-2 rounded-xl border border-slate-700 bg-slate-800/50 p-4 text-center transition-colors hover:border-indigo-500 hover:bg-slate-800">
                  <Camera className="h-5 w-5 text-indigo-400" />
                  <span className="text-xs font-medium text-slate-300">Scatta foto</span>
                  <input ref={inputFotoCameraRef} type="file" accept="image/*" capture="environment" className="hidden" onChange={(e) => handleFotoSelezionata(e.target.files?.[0])} />
                </label>
                <label className="flex flex-1 cursor-pointer flex-col items-center gap-2 rounded-xl border border-slate-700 bg-slate-800/50 p-4 text-center transition-colors hover:border-indigo-500 hover:bg-slate-800">
                  <Images className="h-5 w-5 text-indigo-400" />
                  <span className="text-xs font-medium text-slate-300">Dalla galleria</span>
                  <input ref={inputFotoGalleriaRef} type="file" accept="image/*" className="hidden" onChange={(e) => handleFotoSelezionata(e.target.files?.[0])} />
                </label>
              </div>
            )}

            {suggerimentoAI && !riconoscendoFoto && (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/20 px-2 py-0.5 text-xs font-medium text-emerald-400">
                <Sparkles className="h-3 w-3" /> Riconosciuto sul dispositivo: {suggerimentoAI} (categoria generica, correggi se serve)
              </span>
            )}

            <p className="text-xs text-slate-500">
              Il riconoscimento automatico è generico (categoria, non marca/modello). Per un riconoscimento più preciso usa il pulsante &quot;Apri Google Lens&quot; sulla foto.
            </p>

            <button
              type="button"
              onClick={() => setMostraIncolla((v) => !v)}
              className="flex items-center gap-1.5 text-xs font-medium text-indigo-400 hover:text-indigo-300"
            >
              <ClipboardPaste className="h-3.5 w-3.5" />
              {mostraIncolla ? 'Nascondi' : 'Hai già i risultati di Google Lens? Incollali per estrarre titolo, prezzo e fonte'}
            </button>

            {mostraIncolla && (
              <div className="space-y-2 rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
                <textarea
                  value={testoIncollato}
                  onChange={(e) => setTestoIncollato(e.target.value)}
                  placeholder="Incolla qui l'HTML della pagina Lens (tasto destro sul risultato → Ispeziona → Copy outerHTML) oppure il testo semplice con i prezzi..."
                  rows="4"
                  className="w-full resize-none rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-base text-slate-300 outline-none focus:border-indigo-500"
                />
                <button
                  type="button"
                  onClick={handleEstraiDaTesto}
                  className="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 py-2.5 font-medium text-white hover:bg-emerald-500"
                >
                  <Sparkles className="h-4 w-4" />
                  Estrai prezzi dal testo
                </button>
              </div>
            )}

            <div className="space-y-3 rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={oggetto.marca}
                  onChange={(e) => setOggetto({ ...oggetto, marca: e.target.value })}
                  placeholder="Marca"
                  className="w-1/3 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-base font-semibold text-slate-200 outline-none focus:border-indigo-500"
                />
                <input
                  type="text"
                  required
                  value={oggetto.nome}
                  onChange={(e) => setOggetto({ ...oggetto, nome: e.target.value })}
                  placeholder="Nome / modello dell'oggetto"
                  className="w-2/3 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-base font-semibold text-slate-100 outline-none focus:border-indigo-500"
                />
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={oggetto.categoria}
                  onChange={(e) => setOggetto({ ...oggetto, categoria: e.target.value })}
                  placeholder="Categoria (opzionale)"
                  className="w-1/2 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-base text-slate-300 outline-none focus:border-indigo-500"
                />
                <input
                  type="text"
                  value={oggetto.condizione}
                  onChange={(e) => setOggetto({ ...oggetto, condizione: e.target.value })}
                  placeholder="Condizione (opzionale)"
                  className="w-1/2 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-base text-slate-300 outline-none focus:border-indigo-500"
                />
              </div>
              <textarea
                value={oggetto.descrizione}
                onChange={(e) => setOggetto({ ...oggetto, descrizione: e.target.value })}
                placeholder="Descrizione o dettagli (opzionale)"
                rows="2"
                className="w-full resize-none rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-base text-slate-300 outline-none focus:border-indigo-500"
              />
            </div>

            <button
              type="submit"
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 py-3 font-medium text-white hover:bg-indigo-500"
            >
              <Search className="h-4 w-4" />
              Vedi prezzi di mercato
            </button>
          </form>
        )}

        {fase === FASI.RICERCA && (
          <StatoCaricamento testo="Scansione del mercato in corso..." />
        )}

        {fase === FASI.RISULTATI && statistiche && (
          <>
            <RisultatiPanel
              oggetto={oggetto}
              statistiche={statistiche}
              annunci={annunci}
              prezzoRichiesto={prezzoRichiesto}
              onCalcolaMargine={calcolaMargine}
            />

            {!estensioneInstallata && (
              <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
                <p className="mb-3 text-xs font-medium text-slate-400">
                  Aggiungi altre fonti: apri il sito, poi sui risultati clicca il{' '}
                  <a href="/bookmarklet.html" className="text-indigo-400 hover:text-indigo-300">bookmarklet</a>.
                  {' '}(<a href="/estensione.html" className="text-indigo-400 hover:text-indigo-300">L&apos;estensione lo fa da sola</a>.)
                </p>
                <div className="flex gap-2">
                  {Object.entries(SITI_MERCATO).map(([id, config]) => (
                    <button
                      key={id}
                      type="button"
                      onClick={() => apriSitoMercato(id, oggetto.marca ? `${oggetto.marca} ${oggetto.nome}` : oggetto.nome)}
                      className="flex-1 rounded-lg border border-slate-700 bg-slate-800 py-2 text-xs font-medium text-slate-300 hover:border-indigo-500 hover:text-white"
                    >
                      {config.etichetta}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
          </div>
        )}
      </div>
    </div>
  )
}

function StatoCaricamento({ testo }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-slate-800 bg-slate-900/40 py-16 text-slate-400">
      <Loader2 className="h-6 w-6 animate-spin" />
      <p className="text-sm">{testo}</p>
    </div>
  )
}
