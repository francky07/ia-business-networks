import sys, os
sys.path.append(os.path.expanduser("~/ia_shared"))
from ia_nexus import NexusDB

#!/usr/bin/env python3
import os, time, json, subprocess, requests, threading, re
from datetime import datetime
from web3 import Web3
from collections import Counter

def log(msg): print(f"[BOOSTER_PRO {datetime.now().strftime('%H:%M:%S')}] {msg}")

def load_token():
    with open("ia_net_pro.py") as f:
        for line in f:
            if line.startswith("GITHUB_TOKEN"):
                return line.split('"')[1]
    return None

class ProAgent(threading.Thread):
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

class ProcessSupervisor(ProAgent):
    def execute(self):
        if not any("ia_net_pro.py" in p for p in os.popen("ps aux").read().splitlines()):
            log("⚠️ Bot principal arrêté → redémarrage")
            subprocess.run("tmux new-session -d -s ia_net 'python ia_net_pro.py'", shell=True)
        if not any("ia_booster_pro.py" in p for p in os.popen("ps aux").read().splitlines()):
            log("⚠️ Booster standard arrêté → redémarrage")
            subprocess.run("tmux new-session -d -s booster 'python ia_booster_pro.py'", shell=True)

class BSCMonitor(ProAgent):
    def execute(self):
        try:
            addr = "0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363"
            w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.binance.org"))
            if w3.is_connected():
                bal = w3.from_wei(w3.eth.get_balance(addr), 'ether')
                log(f"💰 Solde BNB: {bal:.8f}")
        except Exception as e: log(f"❌ BSC error: {e}")

class APIChecker(ProAgent):
    def execute(self):
        token = load_token()
        if token:
            r = requests.get("https://api.github.com/user", headers={"Authorization": f"token {token}"})
            if r.status_code == 200: log("✅ GitHub OK")
            else: log("❌ GitHub token invalide")
        try:
            with open("ia_net_pro.py") as f:
                for line in f:
                    if line.startswith("TELEGRAM_BOT_TOKEN"):
                        bot = line.split('"')[1]; break
            if bot:
                r = requests.get(f"https://api.telegram.org/bot{bot}/getMe", timeout=5)
                if r.status_code == 200 and r.json().get("ok"): log("✅ Telegram OK")
                else: log("❌ Telegram KO")
        except: pass
        try:
            with open("ia_net_pro.py") as f:
                for line in f:
                    if line.startswith("OPENAI_API_KEY"):
                        key = line.split('"')[1]; break
            if key:
                r = requests.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {key}"}, timeout=5)
                if r.status_code == 200: log("✅ OpenAI OK")
                else: log("❌ OpenAI KO")
        except: pass

class MemoryCleaner(ProAgent):
    def execute(self):
        mem_file = "ia_mem_pro.json"
        if os.path.exists(mem_file):
            try:
                with open(mem_file) as f:
                    data = json.load(f)
                errors = data.get("errors", [])
                if len(errors) > 100:
                    data["errors"] = errors[-100:]
                    with open(mem_file, "w") as f:
                        json.dump(data, f, indent=2)
                    log("🧹 Nettoyage mémoire (100 dernières erreurs conservées)")
            except: pass

for i in range(100): ProcessSupervisor(f"ProcSup_{i}", 60).start()
for i in range(50): BSCMonitor(f"BSC_{i}", 120).start()
for i in range(50): APIChecker(f"APICheck_{i}", 300).start()
for i in range(50): MemoryCleaner(f"MemClean_{i}", 600).start()

log("🚀 Booster Pro (250 agents) démarré")
while True: time.sleep(30)
