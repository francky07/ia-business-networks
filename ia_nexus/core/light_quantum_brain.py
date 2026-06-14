#!/usr/bin/env python3
"""
Cerveau quantique léger – décision de vente autonome
Sans numpy, scipy, tensorflow – uniquement Python standard
"""
import sqlite3
import json
import os
import random
import time
import subprocess
from datetime import datetime

DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
MEM_PATH = os.path.expanduser("~/ia_nexus/quantum_memory.json")

def load_memory():
    """Charge l'état appris (seuil, historique)"""
    if os.path.exists(MEM_PATH):
        with open(MEM_PATH) as f:
            return json.load(f)
    return {"seuil": 5, "historique": [], "meilleur_score": 0}

def save_memory(mem):
    with open(MEM_PATH, "w") as f:
        json.dump(mem, f)

def get_unsold_count():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM emails WHERE vendu=0")
    count = c.fetchone()[0]
    conn.close()
    return count

def get_recent_revenue(hours=24):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COALESCE(SUM(montant),0) FROM ventes WHERE date > strftime('%s','now','-{} hours')".format(hours))
    rev = c.fetchone()[0]
    conn.close()
    return rev

def simulated_annealing(current_seuil, temp):
    """Recuit simulé : explore un seuil voisin, accepte selon la température"""
    new_seuil = current_seuil + random.randint(-2, 2)
    new_seuil = max(1, min(20, new_seuil))
    # Simuler un score basé sur le revenu des dernières heures
    rev = get_recent_revenue(1)
    current_score = rev / (current_seuil + 1)
    new_score = rev / (new_seuil + 1)
    if new_score > current_score or random.random() < (new_score - current_score) / temp:
        return new_seuil
    return current_seuil

def decide_seuil(mem):
    seuil = mem["seuil"]
    temperature = max(0.1, 1.0 / (1 + len(mem["historique"]) / 50))
    # Exploration / exploitation
    if random.random() < 0.2:  # exploration 20%
        seuil = random.randint(1, 15)
    else:
        seuil = simulated_annealing(seuil, temperature)
    return seuil

def compute_reward():
    """Récompense basée sur le revenu des dernières minutes"""
    rev = get_recent_revenue(1)
    return rev

def update_memory(mem, seuil, reward):
    """Mémorise l'action et ajuste le seuil si la récompense est meilleure"""
    mem["historique"].append({"seuil": seuil, "reward": reward, "time": time.time()})
    if len(mem["historique"]) > 100:
        mem["historique"] = mem["historique"][-100:]
    # Si la récompense est meilleure que le meilleur score, on garde le seuil
    if reward > mem["meilleur_score"]:
        mem["meilleur_score"] = reward
        mem["seuil"] = seuil
    else:
        # Sinon, on dévie légèrement le seuil pour éviter la stagnation
        mem["seuil"] = max(1, min(20, seuil + random.randint(-1, 1)))
    save_memory(mem)

def main():
    print("⚛️ Cerveau quantique léger démarré", flush=True)
    mem = load_memory()
    while True:
        nb = get_unsold_count()
        seuil = decide_seuil(mem)
        if nb >= seuil:
            print(f"💡 Vente déclenchée : {nb} emails (seuil {seuil})", flush=True)
            subprocess.run(["python", os.path.expanduser("~/departement_ventes/sell_emails_paypal.py")])
            # Attendre un peu pour laisser la vente s'enregistrer
            time.sleep(10)
            reward = compute_reward()
            update_memory(mem, seuil, reward)
            print(f"📈 Récompense : {reward:.2f} USD", flush=True)
        else:
            print(f"⏳ Attente : {nb} emails < seuil {seuil}", flush=True)
        time.sleep(60)

if __name__ == "__main__":
    main()
