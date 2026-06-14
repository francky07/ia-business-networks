#!/usr/bin/env python3
import os, uuid, requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)
PI_API_BASE = "https://api.minepi.com/v2"
sessions = {}
user_sessions = {}

@app.route("/api/pi/validate", methods=["POST"])
def validate():
    data = request.json
    token = data.get("accessToken")
    if not token: return jsonify({"error": "Token manquant"}), 400
    try:
        r = requests.get(f"{PI_API_BASE}/me", headers={"Authorization": f"Bearer {token}"}, timeout=10)
        if r.status_code != 200: return jsonify({"error": "Token invalide"}), 401
        user = r.json()
        uid = user["uid"]
        session_token = user_sessions.get(uid)
        if not session_token or session_token not in sessions:
            session_token = str(uuid.uuid4())
            sessions[session_token] = {"uid": uid, "username": user["username"]}
            user_sessions[uid] = session_token
        return jsonify({"status": "ok", "sessionToken": session_token, "user": user})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/pi/users", methods=["GET"])
def get_users():
    return jsonify({"users": list(sessions.values())})

if __name__ == "__main__":
    print("✅ Pi Backend démarré sur http://localhost:5002")
    app.run(host="0.0.0.0", port=5002, debug=False)
