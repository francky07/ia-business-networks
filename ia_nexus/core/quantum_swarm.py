#!/usr/bin/env python3
"""
Cerveau quantique avec essaim d'agents (250 neurones + 500 boosters)
Chaque agent propose un seuil, le cerveau central fusionne les votes.
"""
import sqlite3
import json
import os
import random
import time
import subprocess
import asyncio
from collections import Counter

DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
MEM_PATH = os.path.expanduser("~/ia_nexus/quantum_memory.json")

# Paramètres
NB_AGENTS = 250
NB_BOOSTERS = 500
SEUIL_MIN = 1
SEUIL_MAX = 20

# File de propositions
proposal_queue = asyncio.Queue()

def load_memory():
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

def get_recent_revenue(hours=1):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COALESCE(SUM(montant),0) FROM ventes WHERE date > strftime('%s','now','-{} hours')".format(hours))
    rev = c.fetchone()[0]
    conn.close()
    return rev

async def neurone_agent(agent_id, is_booster=False):
    """Un agent (neurone) ou booster qui propose périodiquement un seuil"""
    weight = 2 if is_booster else 1   # les boosters ont un poids double
    while True:
        # Chaque agent observe le stock et propose un seuil basé sur une heuristique simple
        stock = get_unsold_count()
        rev = get_recent_revenue()
        # Heuristique personnalisée (chaque agent a un biais aléatoire)
        if is_booster:
            # Les boosters sont plus agressifs
            base = max(SEUIL_MIN, min(SEUIL_MAX, int(stock / 50) + random.randint(-2, 2)))
        else:
            base = max(SEUIL_MIN, min(SEUIL_MAX, int(stock / 100) + random.randint(-1, 1)))
        # Ajustement selon le revenu récent
        if rev > 0.1:
            base = max(SEUIL_MIN, base - 1)
        seuil = max(SEUIL_MIN, min(SEUIL_MAX, base + random.randint(-2, 2)))
        await proposal_queue.put((seuil, weight))
        # Délai : agents normaux plus lents (2‑5s), boosters plus rapides (0.5‑2s)
        await asyncio.sleep(random.uniform(0.5, 2.0) if is_booster else random.uniform(2.0, 5.0))

async def decision_maker():
    """Fusionne les propositions des agents et boosters pour décider du seuil final"""
    mem = load_memory()
    # Stockage temporaire des votes pondérés
    votes = []
    last_decision_time = time.time()
    while True:
        seuil, weight = await proposal_queue.get()
        votes.extend([seuil] * weight)
        # Toutes les 10 secondes ou si assez de votes, on décide
        if time.time() - last_decision_time > 10 or len(votes) > 100:
            if votes:
                # Vote à la majorité pondérée
                counter = Counter(votes)
                final_seuil = counter.most_common(1)[0][0]
                mem["seuil"] = final_seuil
                save_memory(mem)
                # Afficher un résumé
                nb_agents_actifs = len(set(votes))
                print(f"🧠 Décision collective : seuil = {final_seuil} (basé sur {len(votes)} propositions de {nb_agents_actifs} agents)", flush=True)
                # Réinitialiser les votes
                votes = []
                last_decision_time = time.time()
            else:
                await asyncio.sleep(1)

async def main():
    print(f"⚛️ Lancement de l'essaim : {NB_AGENTS} neurones + {NB_BOOSTERS} boosters", flush=True)
    # Lancer les agents neurones
    for i in range(NB_AGENTS):
        asyncio.create_task(neurone_agent(i, is_booster=False))
    # Lancer les boosters
    for i in range(NB_BOOSTERS):
        asyncio.create_task(neurone_agent(i, is_booster=True))
    # Lancer le décideur central
    asyncio.create_task(decision_maker())

    # Boucle principale de vente (identique à l'ancien cerveau)
    mem = load_memory()
    while True:
        nb = get_unsold_count()
        seuil = mem.get("seuil", 5)
        if nb >= seuil:
            print(f"💡 Vente déclenchée : {nb} emails (seuil collectif = {seuil})", flush=True)
            subprocess.run(["python", os.path.expanduser("~/departement_ventes/sell_emails_paypal.py")])
            time.sleep(10)
            reward = get_recent_revenue(1)
            # Mémoriser le résultat (renforcement)
            mem["historique"].append({"seuil": seuil, "reward": reward, "time": time.time()})
            if reward > mem.get("meilleur_score", 0):
                mem["meilleur_score"] = reward
            save_memory(mem)
            print(f"📈 Récompense : {reward:.2f} USD", flush=True)
        else:
            print(f"⏳ Attente : {nb} emails < seuil {seuil}", flush=True)
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
