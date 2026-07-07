📁 Multi‑Protocol Honeypot with Attack Analytics

Description
Emulates SSH (port 2222) and HTTP (port 8080) services, logs all connection attempts, captures credentials, and enriches attacker IPs with geolocation (MaxMind GeoIP). Sends alerts to a separate dashboard.

1. Navigate to the project folder.

2. Create a virtual environment (recommended):
bash

python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

    Install dependencies – each project has its own requirements.txt or lists the required packages.

    Run the main script as described in the project’s section.

    Note: Some projects require system tools (e.g., nmap, subfinder, httpx, zeek). Installation instructions are provided per project.

Core Technologies

    Twisted, GeoIP2, Flask‑SocketIO

Features

    SSH emulator (logs username/password attempts)

    HTTP honeypot (logs paths, POST data, user‑agents)

    Geolocation lookup for each source IP

    Real‑time dashboard for attack feed

Installation & Setup
bash

pip install twisted geoip2 flask flask-socketio eventlet
# Download GeoLite2‑City.mmdb from MaxMind (free) and place in the project folder.

Usage

    Start the honeypot dashboard (Terminal 1):
    bash

python dashboard_honeypot.py

(listens on port 5001)

Run the honeypot (Terminal 2):
bash

python honeypot.py

Testing

    SSH: ssh -p 2222 user@127.0.0.1 (any password)

    HTTP: curl http://127.0.0.1:8080/login -X POST -d "user=test"

    Alerts appear on the dashboard (http://127.0.0.1:5001).

