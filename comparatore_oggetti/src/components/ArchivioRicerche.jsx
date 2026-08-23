import { useState, useEffect } from 'react'
import { getRicercheSalvate, eliminaRicerca } from '../services/dbService.js'
import { notifichePushSupportate, statoSottoscrizionePush, attivaNotifichePush, disattivaNotifichePush } from '../services/pushService.js'
import { BellRing, BellOff, Clock, AlertTriangle, CheckCircle2, Trash2 } from 'lucide-react'

function euro(valore) {
  if (valore === null || valore === undefined) return '—'
  return parseFloat(valore).toLocaleString('it-IT', { style: 'currency', currency: 'EUR' })
}

export default function ArchivioRicerche() {
  const [ricerche, setRicerche] = useState([])
  const [loading, setLoading] = useState(true)
  const [errore, setErrore] = useState(null)
  const [pushAttivo, setPushAttivo] = useState(false)
  const [pushCaricamento, setPushCaricamento] = useState(false)

  useEffect(() => {
    async function caricaDati() {
      try {
        const dati = await getRicercheSalvate()
        setRicerche(dati)
      } catch (e) {
        setErrore(e.message)
      } finally {
        setLoading(false)
      }
    }
    caricaDati()
    if (notifichePushSupportate()) {
      statoSottoscrizionePush().then(setPushAttivo)
    }
  }, [])

  async function handleElimina(id) {
    if (!window.confirm('Eliminare questo oggetto dal monitoraggio?')) return
    try {
      await eliminaRicerca(id)
      setRicerche(prev => prev.filter(r => r.id !== id))
    } catch (e) {
      setErrore(e.message)
    }
  }

  async function handleTogglePush() {
    setPushCaricamento(true)
    try {
      if (pushAttivo) {
        await disattivaNotifichePush()
        setPushAttivo(false)
      } else {
        await attivaNotifichePush()
        setPushAttivo(true)
      }
    } catch (e) {
      alert(e.message)
    } finally {
      setPushCaricamento(false)
    }
  }

  const pulsanteNotifiche = notifichePushSupportate() && (
    <button
      onClick={handleTogglePush}
      disabled={pushCaricamento}
      className={`flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors disabled:opacity-50 ${
        pushAttivo
          ? 'border-emerald-500/30 bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30'
          : 'border-slate-700 bg-slate-800/50 text-slate-300 hover:border-indigo-500 hover:bg-slate-800'
      }`}
    >
      {pushAttivo ? <BellRing className="w-3.5 h-3.5" /> : <BellOff className="w-3.5 h-3.5" />}
      {pushAttivo ? 'Notifiche attive' : 'Attiva notifiche'}
    </button>
  )

  if (loading) {
    return <div className="text-slate-400 py-10 text-center animate-pulse">Caricamento archivio in corso...</div>
  }

  if (errore) {
    return (
      <div className="flex items-center gap-2 text-rose-400 py-10 justify-center">
        <AlertTriangle className="w-5 h-5" /> Errore: {errore}
      </div>
    )
  }

  if (ricerche.length === 0) {
    return (
      <div className="space-y-4">
        <div className="flex justify-end">{pulsanteNotifiche}</div>
        <div className="text-slate-500 py-16 text-center border-2 border-dashed border-slate-800 rounded-2xl bg-slate-900/40">
          Nessun oggetto attualmente in monitoraggio.
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-medium text-slate-300">Oggetti Monitorati ({ricerche.length})</h2>
        {pulsanteNotifiche}
      </div>

      {ricerche.map(r => {
        const calato = r.prezzo_corrente !== null && parseFloat(r.prezzo_corrente) <= parseFloat(r.prezzo_bersaglio);

        return (
          <div key={r.id} className={`rounded-2xl border p-5 transition-all ${calato ? 'border-emerald-500/50 bg-emerald-950/20' : 'border-slate-800 bg-slate-900/60'}`}>
            <div className="flex justify-between items-start mb-3">
              <h3 className="font-semibold text-slate-100 text-lg leading-tight pr-4">{r.nome_oggetto}</h3>
              <div className="shrink-0 flex items-center gap-2">
                {calato ? (
                  <span className="flex items-center gap-1.5 rounded-full bg-emerald-500/20 px-2.5 py-1 text-xs font-semibold text-emerald-400 border border-emerald-500/30">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Target Raggiunto
                  </span>
                ) : (
                  <span className="flex items-center gap-1.5 rounded-full bg-indigo-500/20 px-2.5 py-1 text-xs font-medium text-indigo-300 border border-indigo-500/30">
                    <BellRing className="w-3 h-3 animate-pulse" /> In monitoraggio
                  </span>
                )}
                <button
                  onClick={() => handleElimina(r.id)}
                  aria-label="Elimina dal monitoraggio"
                  className="rounded-full p-1.5 text-slate-500 transition-colors hover:bg-rose-500/20 hover:text-rose-400"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mt-5 bg-slate-950/50 p-4 rounded-xl">
              <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold mb-1">Target di Acquisto</p>
                <p className="text-2xl font-bold text-slate-200">{euro(r.prezzo_bersaglio)}</p>
              </div>
              <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold mb-1">Miglior Prezzo Ora</p>
                <p className={`text-2xl font-bold ${calato ? 'text-emerald-400' : 'text-slate-200'}`}>
                  {r.prezzo_corrente ? euro(r.prezzo_corrente) : 'In attesa...'}
                </p>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800/50 flex items-center gap-2 text-xs text-slate-500">
              <Clock className="w-4 h-4" /> 
              Ultimo controllo automatico: {r.ultimo_controllo ? new Date(r.ultimo_controllo + 'Z').toLocaleString('it-IT') : 'Appena inserito'}
            </div>
          </div>
        )
      })}
    </div>
  )
}
