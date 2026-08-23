import React, { useState, useEffect } from 'react';
import { Fingerprint } from 'lucide-react';
import { API_BASE, AUTH_STORAGE_KEY } from '../config.js';
import SmartTurnoHome from './SmartTurnoHome.jsx';

const AUTH_API_BASE = API_BASE;
const STORAGE_KEY = AUTH_STORAGE_KEY;
const PIN_RE = /^\d{4,6}$/;

export default function AuthGate({ children }) {
  const [savedEmail, setSavedEmail] = useState(() => localStorage.getItem(STORAGE_KEY));
  const [showSplash, setShowSplash] = useState(true);
  const [step, setStep] = useState("email"); // email | login | register
  const [email, setEmail] = useState("");
  const [pin, setPin] = useState("");
  const [pin2, setPin2] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (savedEmail) {
    return children;
  }

  if (showSplash) {
    return <SmartTurnoHome onFinish={() => setShowSplash(false)} />;
  }

  const submitEmail = async (e) => {
    e.preventDefault();
    setError("");
    const clean = email.trim().toLowerCase();
    if (!clean.includes("@")) {
      setError("Inserisci un indirizzo email valido.");
      return;
    }
    setBusy(true);
    try {
      const r = await fetch(`${AUTH_API_BASE}/api/auth/exists?email=${encodeURIComponent(clean)}`);
      const { exists } = await r.json();
      setEmail(clean);
      setStep(exists ? "login" : "register");
    } catch {
      setError("Impossibile contattare il server. Controlla la connessione e riprova.");
    } finally {
      setBusy(false);
    }
  };

  const submitLogin = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const r = await fetch(`${AUTH_API_BASE}/api/auth/check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, pin }),
      });
      const data = await r.json();
      if (data.ok) {
        localStorage.setItem(STORAGE_KEY, email);
        setSavedEmail(email);
      } else if (data.reason === "wrongpin") {
        setError("PIN errato. Se non lo ricordi, contatta l'amministratore per recuperarlo.");
      } else {
        setError("Accesso non trovato. Riprova con la tua email.");
        setStep("email");
      }
    } catch {
      setError("Impossibile contattare il server. Controlla la connessione e riprova.");
    } finally {
      setBusy(false);
    }
  };

  const submitRegister = async (e) => {
    e.preventDefault();
    setError("");
    if (!PIN_RE.test(pin)) {
      setError("Il PIN deve avere da 4 a 6 cifre.");
      return;
    }
    if (pin !== pin2) {
      setError("I due PIN non coincidono.");
      return;
    }
    setBusy(true);
    try {
      const r = await fetch(`${AUTH_API_BASE}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, pin }),
      });
      const data = await r.json();
      if (data.ok) {
        localStorage.setItem(STORAGE_KEY, email);
        setSavedEmail(email);
      } else if (data.reason === "exists") {
        setError("Questo indirizzo ha gia' un PIN impostato.");
        setStep("login");
      } else if (data.reason === "notallowed") {
        setError("Questa email non e' autorizzata. Contatta l'amministratore per essere abilitato.");
      } else {
        setError("Dati non validi, controlla email e PIN.");
      }
    } catch {
      setError("Impossibile contattare il server. Controlla la connessione e riprova.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={styles.wrap}>
      <div style={styles.card}>
        <div className="fingerprint-glow-ring">
          <Fingerprint size={40} className="fingerprint-glow-icon" />
        </div>
        <div style={styles.logo}>SmartTurnoArriva</div>

        {step === "email" && (
          <form onSubmit={submitEmail}>
            <p style={styles.hint}>Inserisci la tua email per accedere.</p>
            <input
              style={styles.input}
              type="email"
              placeholder="nome@esempio.it"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoFocus
              required
            />
            {error && <div style={styles.error}>{error}</div>}
            <button style={styles.button} disabled={busy} type="submit">
              {busy ? "Verifica..." : "Continua"}
            </button>
          </form>
        )}

        {step === "login" && (
          <form onSubmit={submitLogin}>
            <p style={styles.hint}>Bentornato, inserisci il tuo PIN.</p>
            <input
              style={styles.input}
              type="password"
              inputMode="numeric"
              placeholder="PIN"
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/\D/g, ""))}
              maxLength={6}
              autoFocus
              required
            />
            {error && <div style={styles.error}>{error}</div>}
            <button style={styles.button} disabled={busy} type="submit">
              {busy ? "Verifica..." : "Accedi"}
            </button>
            <button
              type="button"
              style={styles.linkButton}
              onClick={() => { setStep("email"); setPin(""); setError(""); }}
            >
              Non sono io
            </button>
          </form>
        )}

        {step === "register" && (
          <form onSubmit={submitRegister}>
            <p style={styles.hint}>Prima volta qui: crea un PIN (4-6 cifre) per accedere in futuro.</p>
            <input
              style={styles.input}
              type="password"
              inputMode="numeric"
              placeholder="Nuovo PIN"
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/\D/g, ""))}
              maxLength={6}
              autoFocus
              required
            />
            <input
              style={styles.input}
              type="password"
              inputMode="numeric"
              placeholder="Conferma PIN"
              value={pin2}
              onChange={(e) => setPin2(e.target.value.replace(/\D/g, ""))}
              maxLength={6}
              required
            />
            {error && <div style={styles.error}>{error}</div>}
            <button style={styles.button} disabled={busy} type="submit">
              {busy ? "Creazione..." : "Crea accesso"}
            </button>
          </form>
        )}

        <p style={styles.footer}>
          PIN dimenticato? Contatta l'amministratore per recuperarlo.
        </p>
      </div>
    </div>
  );
}

const styles = {
  wrap: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "var(--bg-dark)",
    padding: 16,
  },
  card: {
    width: "100%",
    maxWidth: 360,
    background: "var(--bg-card)",
    border: "1px solid var(--border-color)",
    borderRadius: 12,
    padding: 24,
  },
  logo: {
    color: "var(--accent-cyan)",
    fontWeight: 700,
    fontSize: 20,
    textAlign: "center",
    marginBottom: 16,
  },
  hint: {
    color: "var(--text-muted)",
    fontSize: 14,
    marginBottom: 12,
  },
  input: {
    width: "100%",
    boxSizing: "border-box",
    background: "var(--bg-dark)",
    border: "1px solid var(--border-color)",
    borderRadius: 8,
    color: "var(--text-main)",
    padding: "10px 12px",
    fontSize: 15,
    marginBottom: 10,
  },
  button: {
    width: "100%",
    background: "var(--accent-cyan)",
    border: "none",
    borderRadius: 8,
    color: "var(--bg-dark)",
    fontWeight: 600,
    padding: "10px 12px",
    fontSize: 15,
    cursor: "pointer",
  },
  linkButton: {
    width: "100%",
    background: "none",
    border: "none",
    color: "var(--text-muted)",
    fontSize: 13,
    padding: "10px 0 0",
    cursor: "pointer",
    textDecoration: "underline",
  },
  error: {
    color: "var(--accent-red)",
    fontSize: 13,
    marginBottom: 10,
  },
  footer: {
    color: "var(--text-muted)",
    fontSize: 12,
    textAlign: "center",
    marginTop: 16,
  },
};
