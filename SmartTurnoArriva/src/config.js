// URL assoluto del server: necessario perche' l'app nativa (Capacitor)
// carica gli asset localmente e un fetch relativo non raggiungerebbe il
// server vero. Dominio stabile (nginx + certbot su questa VPS) - non
// cambia piu' ad ogni riavvio del tunnel.
export const API_BASE = "https://smartturnoarriva.cupto.it";

// Backend separato per la rotazione turni/autisti (progetto turni-rotazioni),
// stesso dominio cupto.it, stessa admin key di API_BASE/api/auth/admin/*.
export const TURNI_API_BASE = "https://rotazione.cupto.it";

// Email a cui viene mostrato il pulsante di accesso al pannello di
// gestione PIN in fondo all'app.
export const ADMIN_EMAIL = "antony.potenza@gmail.com";

// Stessa chiave usata da AuthGate per "ricordare" l'accesso.
export const AUTH_STORAGE_KEY = "smartturno_auth_email";
