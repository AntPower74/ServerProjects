#!/bin/bash
# Espone il file browser di antonio (porta 4200) su serverantonio.cupto.it
# con doppia protezione: auth_basic nginx + login filebrowser.
# Lanciare con: sudo bash setup_files_antonio.sh
set -e

echo "=== 1. Creo il file delle credenziali nginx (auth_basic) ==="
echo 'antonio:$apr1$G3RNw6Pv$kslDMbN34dV2htrlqYEJ/1' > /etc/nginx/.htpasswd-antonio
chmod 640 /etc/nginx/.htpasswd-antonio
chown root:www-data /etc/nginx/.htpasswd-antonio

echo "=== 2. Creo il sito nginx per serverantonio.cupto.it ==="
cat > /etc/nginx/sites-available/serverantonio.cupto.it << 'NGINXEOF'
server {
    server_name serverantonio.cupto.it;

    location / {
        auth_basic "Accesso riservato";
        auth_basic_user_file /etc/nginx/.htpasswd-antonio;

        proxy_pass http://127.0.0.1:4200;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 0;
        proxy_request_buffering off;
        proxy_read_timeout 3600s;
    }

    listen 80;
}
NGINXEOF

ln -sf /etc/nginx/sites-available/serverantonio.cupto.it /etc/nginx/sites-enabled/serverantonio.cupto.it
nginx -t
systemctl reload nginx

echo "=== 3. Certificato SSL (richiede che il DNS di serverantonio.cupto.it punti gia' a questo server: 169.58.70.214) ==="
certbot --nginx -d serverantonio.cupto.it --non-interactive --agree-tos -m antony.potenza@gmail.com

echo "=== Fatto. Verifica: ==="
curl -sI https://serverantonio.cupto.it | head -3
