#!/usr/bin/env python3
import os, time, json, threading, requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

data_lock = threading.Lock()
shared_data = {
    "bots": {},
    "global_state": {
        "last_cycle": 0,
        "last_action": "",
        "bnb_balance": 0.0,
        "services": {"github": False, "telegram": False, "openai": False}
    },
    "messages": []
}

PING_TIMEOUT = 60
CLEANUP_INTERVAL = 30

def log(msg):
    print(f"[HUB {datetime.now().strftime('%H:%M:%S')}] {msg}")

def cleanup_dead_bots():
    now = time.time()
    with data_lock:
        dead = [bid for bid, info in shared_data["bots"].items() if now - info.get("last_ping", 0) > PING_TIMEOUT]
        for bid in dead:
            del shared_data["bots"][bid]
            log(f"🧹 Bot {bid} supprimé (timeout)")

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    bot_id = data.get('bot_id')
    if not bot_id:
        return jsonify({"error": "bot_id required"}), 400
    with data_lock:
        shared_data["bots"][bot_id] = {
            "last_ping": time.time(),
            "status": "active",
            "registered_at": datetime.now().isoformat(),
            "info": data.get("info", {})
        }
    log(f"📡 Bot {bot_id} enregistré")
    return jsonify({"status": "ok"})

@app.route('/api/ping', methods=['POST'])
def ping():
    data = request.json
    bot_id = data.get('bot_id')
    if not bot_id:
        return jsonify({"error": "bot_id required"}), 400
    state = data.get('state', {})
    with data_lock:
        if bot_id not in shared_data["bots"]:
            shared_data["bots"][bot_id] = {"registered_at": datetime.now().isoformat()}
        shared_data["bots"][bot_id]["last_ping"] = time.time()
        shared_data["bots"][bot_id]["status"] = "active"
        shared_data["bots"][bot_id]["state"] = state
        if "cycle" in state:
            shared_data["global_state"]["last_cycle"] = state["cycle"]
        if "balance" in state:
            shared_data["global_state"]["bnb_balance"] = state["balance"]
        if "last_action" in state:
            shared_data["global_state"]["last_action"] = state["last_action"]
    return jsonify({"status": "pong"})

@app.route('/api/get_state', methods=['GET'])
def get_state():
    with data_lock:
        state = {
            "bots": {bid: {"status": info.get("status"), "last_ping": info.get("last_ping"), "state": info.get("state", {})}
                     for bid, info in shared_data["bots"].items()},
            "global": shared_data["global_state"].copy()
        }
    return jsonify(state)

@app.route('/api/broadcast', methods=['POST'])
def broadcast():
    data = request.json
    msg = data.get('message')
    sender = data.get('sender', 'unknown')
    if not msg:
        return jsonify({"error": "message required"}), 400
    with data_lock:
        shared_data["messages"].append({"from": sender, "text": msg, "time": datetime.now().isoformat()})
        if len(shared_data["messages"]) > 100:
            shared_data["messages"] = shared_data["messages"][-100:]
    log(f"📢 Broadcast de {sender}: {msg[:50]}")
    return jsonify({"status": "broadcasted"})

@app.route('/api/get_messages', methods=['GET'])
def get_messages():
    limit = request.args.get('limit', 20, type=int)
    with data_lock:
        msgs = shared_data["messages"][-limit:]
    return jsonify({"messages": msgs})

def cleanup_loop():
    while True:
        time.sleep(CLEANUP_INTERVAL)
        cleanup_dead_bots()

if __name__ == "__main__":
    threading.Thread(target=cleanup_loop, daemon=True).start()
    log("🚀 Antenne relais démarrée sur http://localhost:5003")
    app.run(host="0.0.0.0", port=5003, debug=False, threaded=True)
