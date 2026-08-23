import clsx from 'clsx'

const STILI = {
  alta: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  media: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
  bassa: 'bg-rose-500/15 text-rose-400 border-rose-500/30'
}

const ETICHETTE = {
  alta: 'Alta vendibilità',
  media: 'Vendibilità media',
  bassa: 'Bassa vendibilità'
}

export default function BadgeVendibilita({ livello }) {
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full border px-3 py-1 text-sm font-medium',
        STILI[livello]
      )}
    >
      {ETICHETTE[livello]}
    </span>
  )
}
