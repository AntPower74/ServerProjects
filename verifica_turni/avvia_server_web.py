#!/usr/bin/env python3
import http.server
import socketserver
import urllib.parse
import os
import sys
import json
import subprocess

PORT = 8085
DIRECTORY = "/home/antonio/verifica_turni/web"
sys.path.append("/home/antonio/verifica_turni")

from pdf_generator_dinamico import genera_pdf_bytes
from motore_generatore_set_alternativi import genera_nuovo_set
STATUS_FILE = "/home/antonio/verifica_turni/web/optimizer_status.json"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ['/api/genera_pdf', '/api/rigenera_turni', '/api/avvia_ottimo_globale', '/api/ottimo_globale_status']:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json' if 'pdf' not in parsed.path else 'application/pdf')
            self.end_headers()
            return
        super().do_HEAD()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        # 1. API PDF
        if parsed.path == '/api/genera_pdf':
            qs = urllib.parse.parse_qs(parsed.query)
            params = {k: v[0] for k, v in qs.items()}
            try:
                pdf_bytes = genera_pdf_bytes(params)
                self.send_response(200)
                self.send_header('Content-Type', 'application/pdf')
                self.send_header('Content-Disposition', f'inline; filename="Dossier_Turni_{params.get("dep","TPL")}_2026.pdf"')
                self.send_header('Content-Length', str(len(pdf_bytes)))
                self.end_headers()
                self.wfile.write(pdf_bytes)
                return
            except Exception as e:
                print("Errore generazione PDF dinamico:", e)
                self.send_error(500, f"Errore generazione PDF: {e}")
                return

        # 2. API AVVIO OTTIMIZZATORE OR-TOOLS C++ (Subprocess isolato con Min & Max)
        if parsed.path == '/api/avvia_ottimo_globale':
            qs = urllib.parse.parse_qs(parsed.query)
            min_lavoro = int(qs.get('min_lavoro', [390])[0])
            max_nastro = int(qs.get('max_nastro', [630])[0])
            
            subprocess.Popen([
                sys.executable,
                "/home/antonio/verifica_turni/motore_ottimo_globale_ortools.py",
                str(min_lavoro),
                str(max_nastro)
            ])
            
            resp = json.dumps({'status': 'started', 'message': 'Ottimizzatore Google OR-Tools avviato in processo isolato'}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        # 3. API STATO / PROGRESS BAR OTTIMIZZATORE
        if parsed.path == '/api/ottimo_globale_status':
            try:
                if os.path.exists(STATUS_FILE):
                    with open(STATUS_FILE) as f:
                        resp = f.read().encode('utf-8')
                else:
                    resp = json.dumps({'progress': 0, 'step': 'In attesa...', 'status': 'idle'}).encode('utf-8')
                    
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Content-Length', str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
                return
            except Exception as e:
                self.send_error(500, f"Errore status: {e}")
                return

        # 4. API RIGENERAZIONE RAPIDA
        if parsed.path == '/api/rigenera_turni':
            qs = urllib.parse.parse_qs(parsed.query)
            min_lavoro = int(qs.get('min_lavoro', [390])[0])
            max_nastro = int(qs.get('max_nastro', [630])[0])
            strategia = qs.get('strategia', ['bilanciato'])[0]
            
            try:
                nuovo_set = genera_nuovo_set(min_lavoro, max_nastro, strategia)
                with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
                    json.dump(nuovo_set, f, ensure_ascii=False, indent=2)
                
                resp = json.dumps({
                    'status': 'ok',
                    'count': len(nuovo_set),
                    'strategia': strategia,
                    'message': f"Generato con successo nuovo set di {len(nuovo_set)} turni (Strategia: {strategia.capitalize()})"
                }).encode('utf-8')
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
                return
            except Exception as e:
                print("Errore rigenerazione turni:", e)
                self.send_error(500, f"Errore: {e}")
                return
        
        super().do_GET()

socketserver.TCPServer.allow_reuse_address = True
print(f"🚀 SERVER WEB & OR-TOOLS SOLVER ATTIVO SU PORTA: {PORT}")

with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    httpd.serve_forever()
