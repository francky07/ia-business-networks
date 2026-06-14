#!/usr/bin/env python3
import os, subprocess, json, time, requests, base64
from dotenv import load_dotenv

LOG_FILE = os.path.expanduser("~/depannage.log")
KEYS_FILE = os.path.expanduser("~/agence_kays/keys.json")
ENV_FILE = os.path.expanduser("~/.env_ia_business")
SESSIONS = {"agence_kays": "cd ~/agence_kays && python agence.py", "ventes": "cd ~/departement_ventes && python ventes.py"}

def log(msg): print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def is_tmux_running(s): return s in subprocess.run(["tmux", "ls"], capture_output=True, text=True).stdout
def restart(s, cmd): subprocess.run(["tmux", "kill-session", "-t", s], capture_output=True); time.sleep(1); subprocess.run(["tmux", "new-session", "-d", "-s", s, cmd], shell=True); log(f"✅ {s} redémarré")

def check_keys():
    if not os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, "w") as f: json.dump({"emails": [], "github_tokens": []}, f, indent=2)
        log("📁 keys.json recréé")
    else:
        try: data = json.load(open(KEYS_FILE))
        except: data = {"emails": [], "github_tokens": []}
        if "emails" not in data: data["emails"] = []; json.dump(data, open(KEYS_FILE, "w")); log("🔧 keys.json réparé")

def check_paypal():
    load_dotenv(ENV_FILE)
    cid = os.getenv("PAYPAL_CLIENT_ID"); sec = os.getenv("PAYPAL_CLIENT_SECRET"); mode = os.getenv("PAYPAL_MODE","sandbox")
    if not cid or not sec: log("⚠️ PayPal clés manquantes"); return
    base = "https://api-m.sandbox.paypal.com" if mode=="sandbox" else "https://api-m.paypal.com"
    try:
        auth = base64.b64encode(f"{cid}:{sec}".encode()).decode()
        r = requests.post(f"{base}/v1/oauth2/token", headers={"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded", "Accept":"application/json"}, data={"grant_type":"client_credentials"}, timeout=10)
        if r.status_code==200: log("✅ PayPal OK")
        else: log(f"⚠️ PayPal erreur {r.status_code}")
    except Exception as e: log(f"❌ PayPal: {e}")

def main():
    log("🛡️ DÉPANNAGE DÉMARRÉ")
    while True:
        for s,cmd in SESSIONS.items():
            if not is_tmux_running(s): restart(s,cmd)
        check_keys()
        if int(time.time()) % 600 < 30: check_paypal()
        time.sleep(30)
if __name__ == "__main__":
    main()
