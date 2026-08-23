#!/bin/bash
cat << 'EOF' > /etc/nginx/sites-available/smartturno.conf
server {
    server_name smartturno.calq.it;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Nessuna cache — aggiornamenti immediati su tutti i dispositivi
        add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }
}
EOF

ln -sf /etc/nginx/sites-available/smartturno.conf /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
certbot --nginx -d smartturno.calq.it --non-interactive --agree-tos -m admin@calq.it
echo "Configurazione completata!"
