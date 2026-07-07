#!/usr/bin/env python3
"""
Multi‑Protocol Honeypot (SSH emulator + HTTP) with GeoIP & Real‑time Alerts
"""

import socket
import socketserver
import threading
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import geoip2.database
import socketio

# ---------- CONFIG ----------
SSH_PORT = 2222
HTTP_PORT = 8080
GEOIP_DB = "GeoLite2-City.mmdb"   # download from MaxMind
DASHBOARD_URL = "http://127.0.0.1:5001"

# ---------- SOCKETIO CLIENT ----------
sio = socketio.Client()
try:
    sio.connect(DASHBOARD_URL)
    print("[*] Connected to honeypot dashboard.")
except Exception as e:
    print(f"[!] Dashboard connection failed: {e}")
    print("[!] Alerts will be logged to console only.")

def send_alert(attack_type, src_ip, details):
    """Enrich with GeoIP and send to dashboard."""
    geo = {"country": "Unknown", "city": "Unknown"}
    try:
        with geoip2.database.Reader(GEOIP_DB) as reader:
            resp = reader.city(src_ip)
            geo = {
                "country": resp.country.name,
                "city": resp.city.name,
                "latitude": resp.location.latitude,
                "longitude": resp.location.longitude
            }
    except Exception as e:
        pass

    alert = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": attack_type,
        "src_ip": src_ip,
        "geo": geo,
        "details": details
    }
    try:
        sio.emit('honeypot_alert', alert)
    except:
        pass
    print(f"[+] {attack_type} from {src_ip} ({geo['country']}, {geo['city']}) – {details}")

# ---------- SSH EMULATOR (TCP Server) ----------
class SSHHandler(socketserver.StreamRequestHandler):
    def handle(self):
        client_ip = self.client_address[0]
        send_alert("SSH_CONNECT", client_ip, "connection established")
        # Send fake SSH banner
        self.wfile.write(b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3\r\n")
        # Read any data (credentials)
        try:
            data = self.rfile.read(1024).decode('utf-8', errors='ignore')
            if data:
                send_alert("SSH_ATTACK", client_ip, f"data: {data[:200]}")
        except:
            pass
        self.request.close()

class SSHServer(socketserver.TCPServer):
    allow_reuse_address = True

# ---------- HTTP HONEYPOT ----------
class HTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return  # suppress default logging

    def do_GET(self):
        self._handle_request("GET")

    def do_POST(self):
        self._handle_request("POST")

    def _handle_request(self, method):
        client_ip = self.client_address[0]
        path = self.path
        ua = self.headers.get('User-Agent', '')
        # Read POST data if any
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = ""
        if method == "POST" and content_length:
            post_data = self.rfile.read(content_length).decode('utf-8', errors='ignore')
        details = f"method={method}, path={path}, ua={ua}, data={post_data[:200]}"
        send_alert("HTTP_ATTACK", client_ip, details)
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Server under maintenance</h1></body></html>")

# ---------- START SERVERS ----------
if __name__ == "__main__":
    # Start SSH server in a thread
    ssh_server = SSHServer(('0.0.0.0', SSH_PORT), SSHHandler)
    ssh_thread = threading.Thread(target=ssh_server.serve_forever, daemon=True)
    ssh_thread.start()
    print(f"[*] SSH honeypot listening on port {SSH_PORT}")

    # Start HTTP server in main thread
    http_server = HTTPServer(('0.0.0.0', HTTP_PORT), HTTPHandler)
    print(f"[*] HTTP honeypot listening on port {HTTP_PORT}")
    print("[*] Press Ctrl+C to stop.")
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Stopping...")
        ssh_server.shutdown()
        http_server.shutdown()