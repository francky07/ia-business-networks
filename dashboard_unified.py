#!/usr/bin/env python3
"""
Tableau de bord unique – interroge le hub et affiche l'état de tous les composants.
"""
import requests, json, time, os
from datetime import datetime

HUB_URL = "http://localhost:5003"

def clear():
    os.system('clear')

def get_data():
    try:
        r = requests.get(f"{HUB_URL}/api/get_state", timeout=2)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {}

def main():
    print("🚀 Tableau de bord unifié – appuyez sur Ctrl+C pour quitter")
    while True:
        clear()
        data = get_data()
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║              IA NetSolutions PRO - Tableau de bord unifié          ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        # Bots
        bots = data.get("bots", {})
        if bots:
            print("👥 BOTS CONNECTÉS :")
            for bot_id, info in bots.items():
                state = info.get("state", {})
                last_ping = info.get("last_ping", 0)
                age = int(time.time() - last_ping) if last_ping else 0
                status = "✅" if age < 60 else "⚠️" if age < 120 else "❌"
                print(f"   {status} {bot_id} (ping: il y a {age}s)")
                if bot_id == "ia_net" and "cycle" in state:
                    print(f"      Cycle: {state.get('cycle',0)} | Actions: {state.get('actions',0)} | Erreurs: {state.get('errors',0)}")
                    print(f"      Solde BNB: {state.get('balance',0):.8f}")
                if "latencies" in state:
                    lat = state["latencies"]
                    print(f"      Latences (s) : GitHub={lat.get('github','?')} | Telegram={lat.get('telegram','?')} | OpenAI={lat.get('openai','?')} | BSC={lat.get('bsc','?')}")
                if "errors" in state and state["errors"]:
                    print(f"      Dernières erreurs: {', '.join(state['errors'][-2:])}")
            print("")
        else:
            print("⚠️ Aucun bot connecté.\n")
        # Commandes en attente
        # On n'affiche pas les commandes ici pour ne pas surcharger
        print("🔄 Rafraîchi toutes les 5 secondes (Ctrl+C pour quitter)")
        time.sleep(5)

if __name__ == "__main__":
    main()
