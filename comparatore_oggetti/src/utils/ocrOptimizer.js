/**
 * Pre-processore Immagini Canvas + Pulitore OCR Intelligente per Screenshot Subito/Vinted/Marketplace
 */

// 1. Pre-elaborazione immagine su Canvas (Grayscale, Contrasto, Binarizzazione)
export async function preElaboraImmagineCanvas(file) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')

        // Ridimensionamento bilanciato (max 1200px per velocità e nitidezza ottimale OCR)
        let width = img.width
        let height = img.height
        const MAX_DIM = 1200

        if (width > height && width > MAX_DIM) {
          height = Math.round((height * MAX_DIM) / width)
          width = MAX_DIM
        } else if (height > MAX_DIM) {
          width = Math.round((width * MAX_DIM) / height)
          height = MAX_DIM
        }

        canvas.width = width
        canvas.height = height
        ctx.drawImage(img, 0, 0, width, height)

        const imgData = ctx.getImageData(0, 0, width, height)
        const data = imgData.data

        // Aumento contrasto e conversione scala di grigi ottimizzata per testo
        for (let i = 0; i < data.length; i += 4) {
          const r = data[i]
          const g = data[i + 1]
          const b = data[i + 2]

          // Scala di grigi pesata
          let gray = 0.299 * r + 0.587 * g + 0.114 * b

          // Aumento contrasto (curva a S per separare sfondo da testo scuro/chiaro)
          if (gray > 140) {
            gray = Math.min(255, gray * 1.2)
          } else {
            gray = Math.max(0, gray * 0.75)
          }

          data[i] = gray
          data[i + 1] = gray
          data[i + 2] = gray
        }

        ctx.putImageData(imgData, 0, 0)
        resolve(canvas.toDataURL('image/jpeg', 0.92))
      } catch (err) {
        resolve(file) // Fallback al file originale se il canvas fallisce
      }
    }
    img.onerror = () => resolve(file)
    img.src = URL.createObjectURL(file)
  })
}

// 2. Pulitore Intelligente di Testo OCR (Elimina spazzatura UI Subito/Vinted e corregge errori)
export function pulisciTestoOcr(rawText) {
  if (!rawText) return ''

  let text = rawText
    // Correzioni OCR comuni
    .replace(/\|\s*phone/gi, 'iPhone')
    .replace(/1phone/gi, 'iPhone')
    .replace(/iph0ne/gi, 'iPhone')
    .replace(/sw1tch/gi, 'Switch')
    .replace(/swltch/gi, 'Switch')
    .replace(/nint3ndo/gi, 'Nintendo')
    .replace(/g0pr0/gi, 'GoPro')
    .replace(/j0yc0n/gi, 'Joy-Con')
    .replace(/joy con/gi, 'Joy-Con')
    .replace(/0led/gi, 'OLED')
    .replace(/128\s*gb/gi, '128GB')
    .replace(/256\s*gb/gi, '256GB')
    .replace(/64\s*gb/gi, '64GB')

  // Filtra righe di spazzatura delle interfacce delle app
  const righe = text.split(/\r?\n/)
  const righePulite = []

  const patternSpazzatura = [
    /subito/i,
    /vinted/i,
    /marketplace/i,
    /tuttosubito/i,
    /protezione acquisti/i,
    /invia messaggio/i,
    /fai una proposta/i,
    /acquista ora/i,
    /preferiti/i,
    /condividi/i,
    /segnala/i,
    /inserito il/i,
    /oggi alle/i,
    /ieri alle/i,
    /visualizzazioni/i,
    /recensioni/i,
    /spedizione disponibile/i,
    /spedizione da/i,
    /informazioni sul venditore/i,
    /torino\s*\(?to\)?/i,
    /piemonte/i,
    /cerca su subito/i,
    /categoria/i,
    /stato dell'oggetto/i,
    /dettagli annuncio/i,
    /^\s*[\d:.]+\s*$/, // Orari o numeri singoli isolati
    /^\s*battery\s*$/i,
    /^\s*wifi\s*$/i,
    /^\s*4g\s*$/i,
    /^\s*5g\s*$/i,
    /^\s*lte\s*$/i,
    /^\s*[\W_]+\s*$/ // Righe con solo simboli o trattini
  ]

  for (const riga of righe) {
    const trimmed = riga.trim()
    if (trimmed.length < 2) continue

    let isSpazzatura = false
    for (const pat of patternSpazzatura) {
      if (pat.test(trimmed)) {
        isSpazzatura = true
        break
      }
    }

    if (!isSpazzatura) {
      righePulite.push(trimmed)
    }
  }

  // Se dopo la pulizia è rimasto poco testo, usiamo un fallback
  if (righePulite.length === 0) {
    return rawText.trim()
  }

  return righePulite.join('\n')
}
