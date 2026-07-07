#!/usr/bin/env python3
"""
Dashboard for Honeypot alerts – runs on port 5001.
"""
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

alerts = []

@app.route('/')
def index():
    return render_template('honeypot_dashboard.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected to honeypot dashboard')
    for alert in alerts[-10:]:
        emit('honeypot_alert', alert)

@socketio.on('honeypot_alert')
def handle_alert(data):
    alerts.append(data)
    if len(alerts) > 100:
        alerts.pop(0)
    emit('honeypot_alert', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)