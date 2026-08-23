// Reuses SmartTurnoArriva's existing admin key file - same secret, no new login flow.
// Mirrors readAdminKey()/normKey() from SmartTurnoArriva/vite.config.js exactly.
import fs from 'node:fs';

const ADMIN_KEY_FILE = process.env.ADMIN_KEY_FILE
  || '/home/antonio/SmartTurnoArriva/server-data/admin-key.txt';

const normKey = (k) => String(k || '').replace(/[^0-9a-fA-F]/g, '');

function readAdminKey() {
  try {
    return fs.readFileSync(ADMIN_KEY_FILE, 'utf-8').trim();
  } catch {
    return null;
  }
}

export function requireAdmin(req, res, next) {
  const supplied = normKey(
    req.query.key || (req.headers.authorization || '').replace(/^Bearer\s+/i, '')
  );
  const adminKey = readAdminKey();
  if (!adminKey || supplied !== adminKey) {
    return res.status(403).json({ ok: false, reason: 'forbidden' });
  }
  next();
}
