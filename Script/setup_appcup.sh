#!/bin/bash
cat << 'EOF' > /etc/nginx/sites-available/appcup.calq.it
server {
    server_name appcup.calq.it;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/appcup.calq.it /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
certbot --nginx -d appcup.calq.it --non-interactive --agree-tos -m antonio@calq.it
echo "Configurazione completata!"
