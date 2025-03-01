import os
import time
import threading
import requests
import logging
from datetime import datetime
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from modules._LoggerModule import setup_logging

logger = setup_logging(__name__)

# Global lists/dictionaries for log history and active clients
log_history = []
active_clients = {}

# Custom logging handler to emit logs via SocketIO
class WebSocketHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_history.append(log_entry)
        socketio.emit("log", log_entry)

# Setup Flask application and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Attach the WebSocketHandler to the logger
ws_handler = WebSocketHandler()
ws_handler.setFormatter(
    logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}",
        "%Y-%m-%d %H:%M:%S",
        style="{"
    )
)
logger.addHandler(ws_handler)

# Flask routes and SocketIO event handlers
@app.route("/")
def index():
    return render_template("logs.html")

@app.route("/lostconnection")
def lost_connection():
    return render_template("lost_connection.html")

@socketio.on("connect")
def handle_connect():
    sid = request.sid
    active_clients[sid] = datetime.utcnow()
    logger.info(f"Client connected: {sid}")
    for log in log_history:
        emit("log", log)

@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    if sid in active_clients:
        del active_clients[sid]
    logger.warning(f"Client disconnected: {sid}")

@app.route("/shutdown", methods=["POST"])
def shutdown():
    logger.info("Shutdown command received.")
    shutdown_server = request.environ.get("werkzeug.server.shutdown")
    if shutdown_server:
        shutdown_server()
    logger.info("Shutting down the bot process.")
    os._exit(0)

def run_flask():
    try:
        socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    except Exception as e:
        logger.critical(f"Flask server encountered an error: {e}")

# Start the Flask server in a separate thread
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

def monitor_disconnections():
    while True:
        current_time = datetime.utcnow()
        disconnected_clients = []
        for sid, last_seen in active_clients.items():
            if (current_time - last_seen).total_seconds() > 60:
                disconnected_clients.append(sid)
        with app.app_context():
            for sid in disconnected_clients:
                logger.warning(f"Client {sid} inactive for 60+ seconds. Disconnecting...")
                socketio.emit("disconnect", room=sid)
                del active_clients[sid]
        time.sleep(5)

# Start monitoring client disconnections
monitor_thread = threading.Thread(target=monitor_disconnections, daemon=True)
monitor_thread.start()

def wait_for_flask(max_retries=10, retry_interval=1):
    url = "http://localhost:5000"
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                logger.info("Flask server is running")
                break
        except requests.RequestException:
            retries += 1
            logger.warning(f"Retry {retries}/{max_retries} - Waiting for Flask server...")
            if retries == max_retries:
                logger.critical("Max retries reached. Flask server is not up.")
                logger.exception(
                    ConnectionError("Flask server failed to start after maximum retries.")
                )
        time.sleep(retry_interval)

wait_for_flask(max_retries=10, retry_interval=2)
time.sleep(1)
