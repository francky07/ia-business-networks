#!/usr/bin/env python3
import os, time, json, subprocess, threading, requests
from datetime import datetime

MEM_FILE = "ia_opp_mem.json"
LOG_FILE = "ia_opp_booster.log"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[OPP_BOOSTER {ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_memory():
    try:
        with open(MEM_FILE) as f:
            return json.load(f)
    except:
        return {}

def is_process_running(script):
    return subprocess.run(f"pgrep -f '{script}'", shell=True).returncode == 0

def restart_opp_agents():
    log("🔄 Redémarrage des agents Opportunité")
    subprocess.run("tmux kill-session -t opp_agents 2>/dev/null", shell=True)
    time.sleep(1)
    subprocess.run("tmux new-session -d -s opp_agents 'python ia_opp_agents.py'", shell=True)

class BoosterThread(threading.Thread):
    def __init__(self, name, interval=60):
        super().__init__(daemon=True)
        self.name = name
        self.interval = interval
        self.last_run = 0
    def run(self):
        while True:
            now = time.time()
            if now - self.last_run >= self.interval:
                self.last_run = now
                try:
                    self.execute()
                except Exception as e:
                    log(f"Erreur {self.name}: {e}")
            time.sleep(5)
    def execute(self):
        pass

class ProcessSupervisor(BoosterThread):
    def execute(self):
        if not is_process_running("ia_opp_agents.py"):
            log("⚠️ Agents Opportunité arrêtés → redémarrage")
            restart_opp_agents()

for i in range(200):
    ProcessSupervisor(f"ProcSup_{i}", interval=60).start()

class MemoryAnalyzer(BoosterThread):
    def execute(self):
        mem = load_memory()
        opps = mem.get("opportunities", [])
        if len(opps) > 800:
            mem["opportunities"] = opps[-400:]
            with open(MEM_FILE, "w") as f:
                json.dump(mem, f, indent=2)
            log("🧹 Nettoyage de la mémoire des opportunités")
        if mem.get("stats", {}).get("revenue_total", 0) > 10000:
            log("💰 Objectif de revenu atteint ! (simulation)")

for i in range(150):
    MemoryAnalyzer(f"MemAnalyzer_{i}", interval=300).start()

class StrategyOptimizer(BoosterThread):
    def execute(self):
        mem = load_memory()
        products = mem.get("products", [])
        if products:
            best = max(products, key=lambda x: x.get("price", 0))
            log(f"📈 Produit le plus cher : {best['name']} ({best['price']}€)")
        campaigns = mem.get("campaigns", [])
        if campaigns:
            last = campaigns[-1]
            log(f"🎯 Dernière campagne proposée : {last['type']} (budget {last['budget']}€)")

for i in range(150):
    StrategyOptimizer(f"StratOpt_{i}", interval=600).start()

log("🚀 500 agents booster du département Opportunité & Objectivité démarrés")
while True:
    time.sleep(30)
