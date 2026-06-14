#!/usr/bin/env python3
"""
MEGA BOOSTER – 1000 agents asynchrones pour superviser et booster tous les services.
Tourne en parallèle, indépendant du CEO.
"""
import asyncio
import os
import sys
import subprocess
import time
import json
import glob
import shutil
import sqlite3
import random
import aiohttp
from datetime import datetime

# ==================== CONFIGURATION ====================
DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
LOG_FILE = os.path.expanduser("~/mega_booster_1000.log")
STATE_DIR = os.path.expanduser("~/ia_ceo_state")
os.makedirs(STATE_DIR, exist_ok=True)

# Nombre d'agents (1000)
NB_AGENTS = 50
# Intervalles (en secondes) pour chaque type d'agent
INTERVAL_CHECK_TMUX = 30
INTERVAL_CLEAN_LOGS = 3600
INTERVAL_OPTIMIZE_DB = 21600
INTERVAL_CHECK_DISK = 300
INTERVAL_RESTART_DEAD = 60
INTERVAL_SEND_PING = 120

# Liste des bots essentiels (sessions tmux à surveiller)
ESSENTIAL_BOTS = [
    "agence_kays", "ventes", "ia_net", "booster", "booster_pro", "booster_agence",
    "hub", "hub_client", "opp_auto", "ia_reelle", "oeil_de_dieu", "healing",
    "finance", "finance_booster", "cerebrum", "nexus_brain", "app_auto",
    "mega_scraper", "lead_scraper", "paypal_scanner", "ceo_unified", "ceo_neuronal"
]

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# ==================== TÂCHES DES AGENTS ====================
async def check_tmux_sessions():
    """Vérifie que les sessions tmux essentielles sont actives, les relance si besoin"""
    out = await asyncio.create_subprocess_exec("tmux", "ls", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, _ = await out.communicate()
    active = stdout.decode()
    for bot in ESSENTIAL_BOTS:
        if bot not in active:
            log(f"⚠️ Session {bot} manquante → redémarrage")
            if bot == "agence_kays":
                subprocess.run(["tmux", "new-session", "-d", "-s", "agence_kays", "python ~/agence_kays/agence.py"], shell=True)
            elif bot == "ventes":
                subprocess.run(["tmux", "new-session", "-d", "-s", "ventes", "cd ~/departement_ventes && python ventes.py"], shell=True)
            elif bot == "ia_net":
                subprocess.run(["tmux", "new-session", "-d", "-s", "ia_net", "python ~/ia_net_pro.py"], shell=True)
            elif bot == "ceo_unified":
                subprocess.run(["tmux", "new-session", "-d", "-s", "ceo_unified", "python ~/ia_nexus/ceo_unified.py"], shell=True)
            elif bot == "ceo_neuronal":
                subprocess.run(["tmux", "new-session", "-d", "-s", "ceo_neuronal", "python ~/ia_nexus/ceo_neuronal_booster.py"], shell=True)
            else:
                # tentative générique
                subprocess.run(["tmux", "new-session", "-d", "-s", bot, f"python ~/{bot}.py"], shell=True)

async def clean_old_logs():
    """Supprime les logs de plus de 7 jours"""
    patterns = ["~/ia_ceo_state/*.log", "~/cerebrum/logs/*.log", "~/departement_ventes/*.log", "~/ceo_*.log"]
    now = time.time()
    deleted = 0
    for pattern in patterns:
        for f in glob.glob(os.path.expanduser(pattern)):
            if os.path.isfile(f) and now - os.path.getmtime(f) > 7*86400:
                os.remove(f)
                deleted += 1
    if deleted:
        log(f"🧹 {deleted} anciens logs supprimés")

async def optimize_database():
    """Optimise la base SQLite (VACUUM, REINDEX)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("VACUUM")
        conn.execute("REINDEX")
        conn.close()
        log("✅ Base SQLite optimisée")
    except Exception as e:
        log(f"❌ Erreur optimisation DB: {e}")

async def check_disk_space():
    """Vérifie l'espace disque et alerte si < 500 Mo"""
    try:
        disk = shutil.disk_usage("/")
        free_mb = disk.free / (1024*1024)
        if free_mb < 500:
            log(f"⚠️ Espace disque faible: {free_mb:.0f} Mo")
    except: pass

async def restart_dead_processes():
    """Relance les processus Python qui sont morts (ex: ia_net_pro.py)"""
    dead_scripts = ["ia_net_pro.py", "ia_booster_pro.py", "self_healing.py"]
    ps = await asyncio.create_subprocess_exec("ps", "aux", stdout=asyncio.subprocess.PIPE)
    stdout, _ = await ps.communicate()
    running = stdout.decode()
    for script in dead_scripts:
        if script not in running:
            log(f"🔄 Relance du script {script}")
            subprocess.run(["tmux", "new-session", "-d", "-s", script.replace(".py", ""), f"python ~/{script}"], shell=True)

async def ping_ceo():
    """Envoie un ping au CEO via fichier (pour indiquer que le booster est vivant)"""
    with open(os.path.join(STATE_DIR, "mega_booster_alive.json"), "w") as f:
        json.dump({"timestamp": time.time(), "status": "alive", "agents": NB_AGENTS}, f)

# ==================== AGENTS INDIVIDUELS (coroutines) ====================
async def agent_worker(agent_id, task_func, interval):
    """Un agent exécute une tâche périodiquement"""
    last_run = 0
    while True:
        now = time.time()
        if now - last_run >= interval:
            last_run = now
            try:
                await task_func()
                log(f"Agent {agent_id} : tâche effectuée")
            except Exception as e:
                log(f"Agent {agent_id} erreur: {e}")
        await asyncio.sleep(random.uniform(0.5, 2))  # éviter la congestion

# ==================== LANCEMENT DES 1000 AGENTS ====================
async def main():
    log(f"🚀 Mega Booster : lancement de {NB_AGENTS} agents asynchrones")
    tasks = []
    # Répartition : chaque agent a un rôle basé sur son ID
    for i in range(NB_AGENTS):
        # Assigner un type d'agent selon i
        if i % 4 == 0:
            task = check_tmux_sessions
            interval = INTERVAL_CHECK_TMUX
        elif i % 4 == 1:
            task = clean_old_logs
            interval = INTERVAL_CLEAN_LOGS
        elif i % 4 == 2:
            task = optimize_database
            interval = INTERVAL_OPTIMIZE_DB
        else:
            task = restart_dead_processes
            interval = INTERVAL_RESTART_DEAD
        # quelques agents spéciaux
        if i % 100 == 0:
            task = check_disk_space
            interval = INTERVAL_CHECK_DISK
        tasks.append(agent_worker(i, task, interval))
    # Tâche supplémentaire : ping périodique
    tasks.append(agent_worker(NB_AGENTS, ping_ceo, INTERVAL_SEND_PING))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
