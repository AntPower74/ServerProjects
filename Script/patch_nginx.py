#!/usr/bin/env python3
import subprocess

nginx_conf = """
    location /landing {
        proxy_pass http://127.0.0.1:5000/landing;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
"""

# Read current config
with open('/etc/nginx/sites-available/cup.calq.it', 'r') as f:
    content = f.read()

# Only add if not already present
if '/landing' not in content:
    # Insert before the closing brace of the first server block
    insertion_point = content.find('    location /api/')
    if insertion_point != -1:
        content = content[:insertion_point] + nginx_conf + '\n' + content[insertion_point:]
        with open('/etc/nginx/sites-available/cup.calq.it', 'w') as f:
            f.write(content)
        print("Config updated.")
        result = subprocess.run(['nginx', '-t'], capture_output=True, text=True)
        print(result.stdout, result.stderr)
        subprocess.run(['systemctl', 'reload', 'nginx'])
        print("Nginx reloaded.")
    else:
        print("Insertion point not found.")
else:
    print("Already configured.")
