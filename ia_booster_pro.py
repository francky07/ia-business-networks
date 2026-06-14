import sys, os
sys.path.append(os.path.expanduser("~/ia_shared"))
from ia_nexus import NexusDB

#!/usr/bin/env python3
import os, time, json, subprocess, requests, threading, re
from datetime import datetime
from web3 import Web3

def log(msg): print(f"[BOOSTER PRO {datetime.now().strftime('%H:%M:%S')}] {msg}")

def load_token():
    with open("ia_net_pro.py") as f:
        for line in f:
            if line.startswith("GITHUB_TOKEN"):
                return line.split('"')[1]
    return None

class BoosterAgent(threading.Thread):
    def __init__(self, name, interval=60):
        super().__init__(daemon=True); self.name=name; self.interval=interval; self.last_run=0
    def run(self):
        while True:
            now=time.time()
            if now-self.last_run>=self.interval:
                self.last_run=now
                try: self.execute()
                except Exception as e: log(f"Erreur {self.name}: {e}")
            time.sleep(5)
    def execute(self): pass

class ProcessSupervisor(BoosterAgent):
    def execute(self):
        if not any("ia_net_pro.py" in p for p in os.popen("ps aux").read().splitlines()):
            log("⚠️ Bot principal arrêté → redémarrage")
            subprocess.run("tmux new-session -d -s ia_net 'python ia_net_pro.py'", shell=True)

class GitHubHealth(BoosterAgent):
    def execute(self):
        token = load_token()
        if token:
            r = requests.get("https://api.github.com/user", headers={"Authorization": f"token {token}"})
            if r.status_code == 200: log("✅ GitHub OK")
            else: log("❌ Token GitHub invalide")

class BSCMonitor(BoosterAgent):
    def execute(self):
        try:
            addr = "0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363"
            w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.binance.org"))
            if w3.is_connected():
                bal = w3.from_wei(w3.eth.get_balance(addr), 'ether')
                log(f"💰 Solde BNB: {bal:.8f}")
        except Exception as e: log(f"❌ BSC error: {e}")

for i in range(150): ProcessSupervisor(f"Sup_{i}", 60).start()
for i in range(80): GitHubHealth(f"Git_{i}", 300).start()
for i in range(70): BSCMonitor(f"BSC_{i}", 120).start()

log("🚀 Booster standard (300 agents) démarré")
while True: time.sleep(30)
