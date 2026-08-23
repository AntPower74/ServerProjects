const data = [
    {
        "canale": "ESSELUNGA",
        "codice": "ESSELUNGA24",
        "testo_originale": "🎯 ANNUNCIO MIRATO: Fai la spesa online! Consegna gratuita sul tuo primo ordine Esselunga a casa a Torino e provincia. Spesa minima 40€.",
        "badge": "SPONSORIZZATO ⭐",
        "link": "https://www.esselungaacasa.it"
    },
    {
        "canale": "SATISPAY",
        "codice": "54TORINO",
        "testo_originale": "🎯 ANNUNCIO MIRATO: Paga la tua spesa nei negozi fisici aderenti a Torino e ricevi il 20% di Cashback immediato (Max 15€).",
        "link": "https://www.satispay.com/"
    }
];
function getLogoHtml(channelName) {
    const ch = channelName.toLowerCase();
    if (ch.includes('esselunga')) return 'esselunga';
    return 'generic';
}
data.forEach(coupon => {
    const badgeHtml = coupon.badge ? `<div style="background: ${coupon.badge.includes('SPONSORIZZATO') ? '#f59e0b' : '#3b82f6'};">${coupon.badge}</div>` : '';
    const linkHtml = coupon.link ? `<a href="${coupon.link}">Link</a>` : '';
    console.log(getLogoHtml(coupon.canale));
});
