#!/usr/bin/env python3
import asyncio
import subprocess
import json
import os
import time
import aiohttp
from datetime import datetime
from web3 import Web3

HOME = os.path.expanduser("~")
LOG_FILE = os.path.join(HOME, "supreme_intelligence", "orchestrator.log")
STATE_FILE = os.path.join(HOME, "supreme_intelligence", "state.json")
COMPONENTS = {
    "ia_net": {"script": "ia_net_pro.py", "dir": HOME, "tmux": "ia_net"},
    "booster": {"script": "ia_booster_pro.py", "dir": HOME, "tmux": "booster"},
    "booster_pro": {"script": "ia_booster_pro_250.py", "dir": HOME, "tmux": "booster_pro"},
    "hub": {"script": "ia_hub_advanced.py", "dir": HOME, "tmux": "hub"},
    "hub_client": {"script": "hub_client_advanced.py", "dir": HOME, "tmux": "hub_client"},
    "opp_auto": {"script": "ia_opp_autonomous.py", "dir": HOME, "tmux": "opp_auto"},
    "real_module": {"script": "main.py", "dir": os.path.join(HOME, "ia_mainnet_reelle"), "tmux": "ia_reelle"},
}
if os.path.exists(os.path.join(HOME, "ia_finance_500.py")):
    COMPONENTS["finance"] = {"script": "ia_finance_500.py", "dir": HOME, "tmux": "finance"}
    COMPONENTS["finance_booster"] = {"script": "ia_finance_booster_500.py", "dir": HOME, "tmux": "finance_booster"}

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def tmux_session_exists(session):
    result = subprocess.run(["tmux", "ls"], capture_output=True, text=True)
    return session in result.stdout

def start_component(name, comp):
    script_path = os.path.join(comp["dir"], comp["script"])
    if not os.path.exists(script_path):
        log(f"⚠️ Fichier manquant : {script_path}")
        return False
    subprocess.run(["tmux", "kill-session", "-t", comp["tmux"]], capture_output=True)
    time.sleep(0.5)
    cmd = ["tmux", "new-session", "-d", "-s", comp["tmux"], f"cd {comp['dir']} && python {comp['script']}"]
    subprocess.run(cmd, capture_output=True)
    log(f"✅ {name} démarré (session {comp['tmux']})")
    return True

def monitor_components():
    for name, comp in COMPONENTS.items():
        if not tmux_session_exists(comp["tmux"]):
            log(f"⚠️ Session {comp['tmux']} absente → redémarrage")
            start_component(name, comp)

async def auto_convert():
    wallet_path = os.path.join(HOME, "ia_mainnet_reelle", "wallet.json")
    if not os.path.exists(wallet_path):
        return
    with open(wallet_path) as f:
        data = json.load(f)
    usd = data.get("total_earnings_usd", 0)
    if usd < 0.01:
        return
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=usd") as resp:
            if resp.status == 200:
                price_data = await resp.json()
                bnb_price = price_data["binancecoin"]["usd"]
                bnb_amount = usd / bnb_price
                log(f"💰 Conversion auto: {usd:.2f} USD → {bnb_amount:.8f} BNB")
                data["bnb_balance"] = data.get("bnb_balance", 0) + bnb_amount
                data["total_earnings_usd"] = 0
                with open(wallet_path, "w") as f:
                    json.dump(data, f, indent=2)
                log("✅ Conversion enregistrée")

async def dashboard():
    while True:
        os.system("clear")
        print("════════════════════════════════════════════════════════════════")
        print("  🧠 SUPREME INTELLIGENCE – TABLEAU DE BORD CENTRAL")
        print("════════════════════════════════════════════════════════════════")
        print(f"Heure: {datetime.now().strftime('%H:%M:%S')}\n")
        for name, comp in COMPONENTS.items():
            status = "✅ actif" if tmux_session_exists(comp["tmux"]) else "❌ mort"
            print(f"   {name:12} : {status}")
        state_path = os.path.join(HOME, "ia_mainnet_reelle", "state.json")
        if os.path.exists(state_path):
            with open(state_path) as f:
                s = json.load(f)
            print(f"\n📊 Module réel : cycle {s.get('cycle',0)} | gains USD {s.get('total_earnings_usd',0):.4f}")
        wallet_path = os.path.join(HOME, "ia_mainnet_reelle", "wallet.json")
        if os.path.exists(wallet_path):
            with open(wallet_path) as f:
                w = json.load(f)
            print(f"💰 BNB converti (local) : {w.get('bnb_balance',0):.8f}")
        try:
            w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org"))
            bal = w3.from_wei(w3.eth.get_balance("0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363"), "ether")
            print(f"💰 SOLDE BNB RÉEL : {bal:.8f}")
        except: pass
        print("\n🔄 Rafraîchi toutes les 10s (Ctrl+C pour quitter l'affichage)")
        await asyncio.sleep(10)

async def main_loop():
    log("🚀 Supreme Intelligence orchestrator démarré")
    for name, comp in COMPONENTS.items():
        start_component(name, comp)
    asyncio.create_task(dashboard())
    while True:
        monitor_components()
        await auto_convert()
        await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main_loop())
