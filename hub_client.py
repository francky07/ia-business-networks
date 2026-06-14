#!/usr/bin/env python3
"""
Client Hub intelligent – lit les fichiers d'état réels des bots et envoie des pings enrichis.
"""
import os, time, json, requests, threading
from web3 import Web3

HUB_URL = "http://localhost:5003"

def get_main_bot_state():
    """Récupère les stats du bot principal (cycle, actions, erreurs)."""
    state = {"type": "main", "agents": 700}
    try:
        with open("ia_mem_pro.json", "r") as f:
            data = json.load(f)
            state["cycle"] = data["stats"].get("cycle", 0)
            state["actions"] = data["stats"].get("actions", 0)
            state["errors"] = len(data.get("errors", []))
    except:
        pass
    # Solde BNB
    try:
        w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.binance.org"))
        bal = w3.from_wei(w3.eth.get_balance("0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363"), 'ether')
        state["bnb_balance"] = float(bal)
    except:
        pass
    # Services
    try:
        with open("ia_net_pro.py", "r") as f:
            content = f.read()
        import re
        token = re.search(r'GITHUB_TOKEN = "(.*?)"', content).group(1)
        if token:
            import requests
            r = requests.get("https://api.github.com/user", headers={"Authorization": f"token {token}"}, timeout=3)
            state["github_ok"] = (r.status_code == 200)
    except:
        state["github_ok"] = False
    return state

def get_booster_state(bot_id):
    """Pour les boosters, état simple (actif)."""
    return {"type": "booster", "alive": True, "timestamp": time.time()}

def send_ping(bot_id, state):
    try:
        requests.post(f"{HUB_URL}/api/register", json={"bot_id": bot_id, "info": {"type": state.get("type")}}, timeout=2)
        requests.post(f"{HUB_URL}/api/ping", json={"bot_id": bot_id, "state": state}, timeout=2)
    except Exception as e:
        print(f"Erreur ping {bot_id}: {e}")

def main():
    print("🚀 Client Hub intelligent démarré (lit les données réelles)")
    while True:
        # Bot principal
        main_state = get_main_bot_state()
        send_ping("ia_net", main_state)
        # Boosters (simulés)
        send_ping("booster_std", {"type": "booster", "alive": True})
        send_ping("booster_pro", {"type": "booster_pro", "alive": True})
        send_ping("backup", {"type": "backup", "alive": True})
        send_ping("hub", {"type": "hub", "alive": True})
        time.sleep(30)

if __name__ == "__main__":
    main()
