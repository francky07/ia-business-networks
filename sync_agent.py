#!/usr/bin/env python3
import json
import time
import os
import subprocess
import sys
from datetime import datetime

SHARED_STATE = os.path.expanduser("~/ia_shared_state.json")
LOG_FILE = os.path.expanduser("~/ia_sync_agent.log")
SLEEP = 15  # vérification toutes les 15 secondes

def log(msg):
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(msg)

def load_shared():
    try:
        with open(SHARED_STATE, 'r') as f:
            return json.load(f)
    except:
        return {}

def restart_service(name):
    log(f"📢 Demande de redémarrage du service {name}")
    # Envoi d'une commande via tmux (si la session existe, on la relance)
    # On utilise le moteur All-in-One pour le faire proprement, ou on agit directement.
    subprocess.run(["tmux", "kill-session", "-t", name], capture_output=True)
    time.sleep(1)
    # Relance selon le type (scripts connus)
    if name == "ia_net":
        subprocess.run(["tmux", "new-session", "-d", "-s", "ia_net", "python ia_net_pro.py"])
    elif name == "ia_reelle":
        subprocess.run(["tmux", "new-session", "-d", "-s", "ia_reelle", "cd ~/ia_mainnet_reelle && python main.py"], shell=True)
    elif name == "booster":
        subprocess.run(["tmux", "new-session", "-d", "-s", "booster", "python ia_booster_pro.py"])
    elif name == "booster_pro":
        subprocess.run(["tmux", "new-session", "-d", "-s", "booster_pro", "python ia_booster_pro_250.py"])
    elif name == "hub":
        subprocess.run(["tmux", "new-session", "-d", "-s", "hub", "python ia_hub_advanced.py"])
    elif name == "hub_client":
        subprocess.run(["tmux", "new-session", "-d", "-s", "hub_client", "python hub_client_advanced.py"])
    elif name == "opp_auto":
        subprocess.run(["tmux", "new-session", "-d", "-s", "opp_auto", "python ia_opp_autonomous.py"])
    log(f"✅ Service {name} relancé")

def execute_command(cmd, target):
    """Exécute une commande reçue du fichier partagé"""
    log(f"📟 Commande reçue: {cmd} pour {target}")
    if cmd == "restart":
        restart_service(target)
    elif cmd == "optimize":
        # Exemple: action d'optimisation
        log(f"⚙️ Optimisation déclenchée sur {target}")
        # Ici vous pouvez ajouter votre logique

def main():
    bot_id = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    log(f"🟢 Agent de synchronisation démarré pour {bot_id}")
    last_commands = {}
    while True:
        state = load_shared()
        # Lire les commandes destinées à ce bot
        commands = state.get("commands", [])
        for cmd_obj in commands:
            target = cmd_obj.get("target")
            if target == bot_id or target == "all":
                cmd = cmd_obj.get("cmd")
                if cmd_obj.get("id") not in last_commands:
                    last_commands[cmd_obj.get("id")] = True
                    execute_command(cmd, bot_id)
        # Optionnel: partager l'état local de ce bot (si on le souhaite)
        # Pour l'instant on se contente de lire
        time.sleep(SLEEP)

if __name__ == "__main__":
    main()
