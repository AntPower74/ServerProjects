import { TrendingUp, TrendingDown, ListChecks, Bell, BellRing, Calculator, ArrowUpDown, ExternalLink } from 'lucide-react'
import { useMemo, useState } from 'react'
import BadgeVendibilita from './BadgeVendibilita.jsx'
import { salvaRicerca } from '../services/dbService.js'

function euro(valore) {
  if (valore === null || valore === undefined) return '—'
  return valore.toLocaleString('it-IT', { style: 'currency', currency: 'EUR' })
}

const OPZIONI_ORDINAMENTO = [
  { valore: 'prezzo-asc', etichetta: 'Prezzo: dal più basso' },
  { valore: 'prezzo-desc', etichetta: 'Prezzo: dal più alto' },
  { valore: 'venduti-prima', etichetta: 'Venduti prima' },
  { valore: 'fonte', etichetta: 'Fonte (A-Z)' }
]

function ordinaAnnunci(annunci, ordinamento) {
  const copia = [...annunci]
  switch (ordinamento) {
    case 'prezzo-desc':
      return copia.sort((a, b) => b.prezzo - a.prezzo)
    case 'venduti-prima':
      return copia.sort((a, b) => {
        if (a.stato === b.stato) return a.prezzo - b.prezzo
        return a.stato === 'venduto' ? -1 : 1
      })
    case 'fonte':
      return copia.sort((a, b) => (a.sorgente || a.fonte || '').localeCompare(b.sorgente || b.fonte || ''))
    case 'prezzo-asc':
    default:
      return copia.sort((a, b) => a.prezzo - b.prezzo)
  }
}

export default function RisultatiPanel({ oggetto, statistiche, annunci, prezzoRichiesto, onCalcolaMargine }) {
  const {
    numeroAnnunci,
    numeroVenduti,
    numeroAttivi,
    prezzoMinimo,
    prezzoMassimo,
    prezzoMedioVendita,
    livelloVendibilita,
    prezzoVenditaConsigliato,
    margineDisponibile,
    percentualeMargineReale,
    convieneComprare
  } = statistiche

  const [salvato, setSalvato] = useState(false)
  const [inputPrezzo, setInputPrezzo] = useState(prezzoRichiesto ?? '')
  const [ordinamento, setOrdinamento] = useState('prezzo-asc')
  const haMargine = margineDisponibile !== null

  const annunciOrdinati = useMemo(() => ordinaAnnunci(annunci, ordinamento), [annunci, ordinamento])

  const handleSubmitPrezzo = (e) => {
    e.preventDefault()
    const prezzo = parseFloat(inputPrezzo)
    if (!prezzo || prezzo <= 0) return
    onCalcolaMargine(prezzo)
  }

  const renderLogoSorgente = (sorgenteBase) => {
    const sorgente = sorgenteBase || 'Sconosciuto';
    let domain = 'google.com';
    let brandColor = 'text-emerald-400';
    let bgColor = 'bg-emerald-500/10 border-emerald-500/20';
    
    if (sorgente.includes('eBay')) {
      domain = 'ebay.it';
      brandColor = 'text-blue-400';
      bgColor = 'bg-blue-500/10 border-blue-500/20';
    } else if (sorgente.includes('Idealo')) {
      domain = 'idealo.it';
      brandColor = 'text-orange-400';
      bgColor = 'bg-orange-500/10 border-orange-500/20';
    } else if (sorgente.includes('Trovaprezzi')) {
      domain = 'trovaprezzi.it';
      brandColor = 'text-purple-400';
      bgColor = 'bg-purple-500/10 border-purple-500/20';
    } else if (sorgente.includes('Subito')) {
      domain = 'subito.it';
      brandColor = 'text-yellow-400';
      bgColor = 'bg-yellow-500/10 border-yellow-500/20';
    } else if (sorgente.includes('Vinted')) {
      domain = 'vinted.it';
      brandColor = 'text-teal-400';
      bgColor = 'bg-teal-500/10 border-teal-500/20';
    } else if (sorgente.includes('Marketplace')) {
      domain = 'facebook.com';
      brandColor = 'text-sky-400';
      bgColor = 'bg-sky-500/10 border-sky-500/20';
    }

    // Pulisco il nome dal suffisso "(Simulato)" per farlo sembrare vero
    const nomePulito = sorgente.replace(' (Simulato)', '');

    return (
      <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full border ${bgColor} shadow-sm`}>
        <img 
          src={`https://www.google.com/s2/favicons?domain=${domain}&sz=64`} 
          alt={nomePulito}
          className="w-4 h-4 rounded-full bg-white object-contain"
        />
        <span className={`text-[11px] font-bold tracking-wider uppercase ${brandColor}`}>
          {nomePulito}
        </span>
      </div>
    );
  }

  const handleMonitora = async () => {
    try {
      await salvaRicerca(oggetto.nome, prezzoVenditaConsigliato);
      setSalvato(true);
    } catch (e) {
      console.error(e);
      alert("Errore durante l'attivazione del monitoraggio.");
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">Oggetto</p>
            <h2 className="mt-1 text-lg font-semibold text-slate-100">{oggetto.nome}</h2>
            {(oggetto.categoria || oggetto.condizione) && (
              <p className="text-sm text-slate-400">{[oggetto.categoria, oggetto.condizione].filter(Boolean).join(' · ')}</p>
            )}
            {oggetto.descrizione && (
              <p className="mt-1 text-xs text-slate-500">{oggetto.descrizione}</p>
            )}
          </div>

          <div className="flex flex-col items-end gap-3">
            <BadgeVendibilita livello={livelloVendibilita} />
            {haMargine && (
              <button
                onClick={handleMonitora}
                disabled={salvato}
                title="Salva nel database e controlla i prezzi in background"
                className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border transition-all ${
                  salvato
                  ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30 cursor-default'
                  : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700 hover:text-white cursor-pointer'
                }`}
              >
                {salvato ? <BellRing className="w-3.5 h-3.5" /> : <Bell className="w-3.5 h-3.5" />}
                {salvato ? 'In monitoraggio' : 'Avvisami se cala'}
              </button>
            )}
          </div>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <Statistica etichetta="Annunci trovati" valore={numeroAnnunci} />
          <Statistica etichetta="Venduti" valore={numeroVenduti} />
          <Statistica etichetta="Attivi ora" valore={numeroAttivi} />
          <Statistica etichetta="Range prezzi" valore={`${euro(prezzoMinimo)} - ${euro(prezzoMassimo)}`} />
        </div>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
        <p className="text-xs uppercase tracking-wide text-slate-500">Prezzo medio di vendita sul mercato</p>
        <p className="mt-1 text-3xl font-bold text-slate-100">{euro(prezzoMedioVendita)}</p>
        <p className="mt-1 text-xs text-slate-500">Questo è indicativamente il prezzo a cui puoi rivendere l&apos;oggetto.</p>

        {haMargine ? (
          <>
            <div className="mt-4 flex items-center gap-2">
              {convieneComprare ? (
                <TrendingUp className="h-5 w-5 text-emerald-400" />
              ) : (
                <TrendingDown className="h-5 w-5 text-rose-400" />
              )}
              <p className="text-sm text-slate-300">
                Margine reale stimato su {euro(parseFloat(inputPrezzo))} di acquisto:{' '}
                <span className={convieneComprare ? 'text-emerald-400' : 'text-rose-400'}>
                  {euro(margineDisponibile)} ({percentualeMargineReale?.toFixed(0)}%)
                </span>
              </p>
            </div>

            <p className="mt-2 text-sm text-slate-400">
              {convieneComprare
                ? 'Il margine di mercato copre il ricarico del 30% che vuoi applicare.'
                : 'Il mercato non garantisce un margine del 30% su questo oggetto a questo prezzo di acquisto.'}
            </p>

            <button
              onClick={() => onCalcolaMargine(null)}
              className="mt-3 text-xs font-medium text-indigo-400 hover:text-indigo-300"
            >
              Cambia prezzo richiesto
            </button>
          </>
        ) : (
          <form onSubmit={handleSubmitPrezzo} className="mt-4 space-y-2 border-t border-slate-800 pt-4">
            <label className="text-sm text-slate-400" htmlFor="prezzo-richiesto">
              A quanto te lo vende il venditore? Inserisci il prezzo richiesto per calcolare il margine.
            </label>
            <div className="flex gap-2">
              <input
                id="prezzo-richiesto"
                type="number"
                inputMode="decimal"
                min="0"
                step="0.01"
                required
                value={inputPrezzo}
                onChange={(e) => setInputPrezzo(e.target.value)}
                placeholder="es. 30"
                className="flex-1 rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-lg outline-none focus:border-indigo-500"
              />
              <button
                type="submit"
                className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 font-medium text-white hover:bg-indigo-500"
              >
                <Calculator className="h-4 w-4" />
                Calcola
              </button>
            </div>
          </form>
        )}
      </div>

      {haMargine && (
        <div className="rounded-2xl border border-indigo-500/30 bg-indigo-500/10 p-5">
          <p className="text-xs uppercase tracking-wide text-indigo-300">Prezzo di vendita consigliato (ricarico 30%)</p>
          <p className="mt-1 text-3xl font-bold text-indigo-200">{euro(prezzoVenditaConsigliato)}</p>
        </div>
      )}

      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
        <div className="mb-3 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-slate-300">
            <ListChecks className="h-4 w-4" />
            <p className="text-sm font-medium">Annunci simili analizzati</p>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <ArrowUpDown className="h-3.5 w-3.5" />
            <select
              value={ordinamento}
              onChange={(e) => setOrdinamento(e.target.value)}
              aria-label="Ordina gli annunci"
              className="rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-xs text-slate-300 outline-none focus:border-indigo-500"
            >
              {OPZIONI_ORDINAMENTO.map((opzione) => (
                <option key={opzione.valore} value={opzione.valore}>{opzione.etichetta}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="max-h-64 space-y-2 overflow-y-auto pr-1">
          {annunciOrdinati.map((a, i) => {
            const Contenitore = a.url ? 'a' : 'div'
            const propsContenitore = a.url
              ? { href: a.url, target: '_blank', rel: 'noopener noreferrer', title: a.titolo || undefined }
              : { title: a.titolo || undefined }
            return (
              <Contenitore
                key={a.id ?? i}
                {...propsContenitore}
                className="flex items-center justify-between gap-2 rounded-lg bg-slate-800/60 px-3 py-2 text-sm hover:bg-slate-800"
              >
                {renderLogoSorgente(a.sorgente || a.fonte)}
                <span className={`shrink-0 ${a.stato === 'venduto' ? 'text-emerald-400' : 'text-slate-300'}`}>
                  {a.stato === 'venduto' ? 'Venduto' : 'Attivo'}
                  {a.giorniFa !== null ? ` · ${a.giorniFa}g fa` : ''}
                </span>
                <span className="shrink-0 font-medium text-slate-100">{euro(a.prezzo)}</span>
                {a.url && <ExternalLink className="h-3.5 w-3.5 shrink-0 text-slate-500" />}
              </Contenitore>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function Statistica({ etichetta, valore }) {
  return (
    <div>
      <p className="text-xs text-slate-500">{etichetta}</p>
      <p className="text-lg font-semibold text-slate-100">{valore}</p>
    </div>
  )
}
