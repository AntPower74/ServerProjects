#!/bin/bash
# Separazione utenti antonio/cup — da lanciare con: sudo bash separazione_utenti.sh
# Esegue in ordine sicuro: prima sposta il sito pubblico fuori da /home/cup,
# poi rimuove l'accesso incrociato, poi blocca le home, poi sistema i file.
set -e

echo "=== 1. Sposto la root del sito www.cupto.it fuori da /home/cup ==="
mkdir -p /var/www/portfolio
cp -a /home/cup/portfolio/. /var/www/portfolio/
chown -R cup:cup /var/www/portfolio
sed -i 's|root /home/cup/portfolio;|root /var/www/portfolio;|' /etc/nginx/sites-available/cup.calq.it
nginx -t
systemctl reload nginx
echo "-- verifica www.cupto.it:"
curl -s -o /dev/null -w "  %{http_code}\n" https://www.cupto.it

echo "=== 2. Rimuovo cup dal gruppo antonio ==="
gpasswd -d cup antonio || true
echo "-- gruppi di cup ora:"
groups cup

echo "=== 3. Blocco le due home a uso esclusivo del proprietario ==="
chmod 700 /home/antonio
chmod 700 /home/cup

echo "=== 4. Chiudo i file troppo permissivi in /home/cup ==="
chmod 600 /home/cup/filebrowser/filebrowser.db
chmod 750 /home/cup/.local/bin/filebrowser
chmod -R go-w /home/cup/.pm2

echo "=== 5. Riassegno ad antonio i file finiti per errore nella sua home ==="
chown antonio:antonio \
  /home/antonio/verifica_turni/cartellini_4sb025.pdf \
  /home/antonio/verifica_turni/cartellini_cas32.pdf \
  /home/antonio/verifica_turni/8.m3u

echo
echo "=== VERIFICA FINALE ==="
echo -n "cup NON deve vedere antonio: "; sudo -u cup ls /home/antonio >/dev/null 2>&1 && echo "FALLITO (vede ancora)" || echo "OK (bloccato)"
echo -n "antonio NON deve vedere cup: "; sudo -u antonio ls /home/cup >/dev/null 2>&1 && echo "FALLITO (vede ancora)" || echo "OK (bloccato)"
for url in https://smartturnoarriva.cupto.it https://cup.calq.it https://www.cupto.it https://prezzly.cupto.it; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  echo "$url -> $code"
done

echo
echo "Fatto. cup e' ancora nel gruppo 'sudo' (puo' diventare root con password) -- dimmi se vuoi che tolga anche quello."
