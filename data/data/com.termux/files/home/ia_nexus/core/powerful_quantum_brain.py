#!/usr/bin/env python3
"""
Cerveau quantique ×100 – PSO + génétique + Holt‑Winters + Monte Carlo + epsilon
"""
import sqlite3
import json
import os
import random
import time
import subprocess
import math
from collections import deque

# ==================== CONFIGURATION ====================
DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
MEM_PATH = os.path.expanduser("~/ia_nexus/quantum_memory.json")
EPSILON = 0.1            # Taux d'exploration (10% de décisions aléatoires)
SEUIL_MIN = 1
SEUIL_MAX = 20
POPULATION_SIZE = 20
GENERATIONS = 10
MONTE_CARLO_ITER = 100
# =======================================================

def load_memory():
    if os.path.exists(MEM_PATH):
        with open(MEM_PATH) as f:
            return json.load(f)
    return {
        "seuil": 5,
        "historique": [],
        "meilleur_score": 0,
        "pso_best": 5,
        "genetic_best": [0.5]*3,
        "holt_winters": {"level": 0, "trend": 0},
        "pattern_memory": []
    }

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

def get_recent_ventes(limit=50):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT montant, date FROM ventes ORDER BY date DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

# ---------- Holt‑Winters ----------
class HoltWinters:
    @staticmethod
    def predict(series, alpha=0.3, beta=0.1, steps=1):
        if len(series) < 2:
            return series[-1] if series else 0
        level = series[0]
        trend = series[1] - series[0] if len(series) > 1 else 0
        for i in range(1, len(series)):
            prev_level = level
            level = alpha * series[i] + (1 - alpha) * (level + trend)
            trend = beta * (level - prev_level) + (1 - beta) * trend
        return level + steps * trend

# ---------- PSO ----------
class Particle:
    def __init__(self, dim=1):
        self.position = [random.uniform(0, 1) for _ in range(dim)]
        self.velocity = [random.uniform(-0.1, 0.1) for _ in range(dim)]
        self.best_position = self.position[:]
        self.best_score = -float('inf')

    def evaluate(self):
        seuil = int(self.position[0] * (SEUIL_MAX - SEUIL_MIN) + SEUIL_MIN)
        rev = get_recent_revenue(1)
        stock = get_unsold_count()
        return max(0, rev / (seuil + 1) - stock / 1000.0)

def pso_optimize(iterations=30, swarm_size=15):
    dim = 1
    swarm = [Particle(dim) for _ in range(swarm_size)]
    global_best_position = None
    global_best_score = -float('inf')
    for _ in range(iterations):
        for p in swarm:
            score = p.evaluate()
            if score > p.best_score:
                p.best_score = score
                p.best_position = p.position[:]
            if score > global_best_score:
                global_best_score = score
                global_best_position = p.position[:]
        w = 0.7
        c1, c2 = 1.5, 1.5
        for p in swarm:
            for i in range(dim):
                r1, r2 = random.random(), random.random()
                p.velocity[i] = w * p.velocity[i] + c1 * r1 * (p.best_position[i] - p.position[i]) + c2 * r2 * (global_best_position[i] - p.position[i])
                p.position[i] += p.velocity[i]
                p.position[i] = max(0, min(1, p.position[i]))
    if global_best_position is None:
        return 5
    seuil = int(global_best_position[0] * (SEUIL_MAX - SEUIL_MIN) + SEUIL_MIN)
    return max(SEUIL_MIN, min(SEUIL_MAX, seuil))

# ---------- Algo génétique ----------
def genetic_optimize():
    def fitness(genes):
        seuil = int(genes[0] * (SEUIL_MAX - SEUIL_MIN) + SEUIL_MIN)
        rev = get_recent_revenue(1)
        stock = get_unsold_count()
        return rev / (seuil + 1) - stock / 500.0

    population = [[random.random() for _ in range(1)] for __ in range(POPULATION_SIZE)]
    for _ in range(GENERATIONS):
        scored = [(p, fitness(p)) for p in population]
        scored.sort(key=lambda x: x[1], reverse=True)
        best = scored[0][0]
        new_pop = [best[:] for _ in range(2)]
        while len(new_pop) < POPULATION_SIZE:
            p1 = random.choice(scored[:5])[0]
            p2 = random.choice(scored[:5])[0]
            child = [p1[0] if random.random() < 0.5 else p2[0]]
            if random.random() < 0.2:
                child[0] += random.gauss(0, 0.1)
                child[0] = max(0, min(1, child[0]))
            new_pop.append(child)
        population = new_pop
    best_genes = max(population, key=lambda p: fitness(p))
    seuil = int(best_genes[0] * (SEUIL_MAX - SEUIL_MIN) + SEUIL_MIN)
    return max(SEUIL_MIN, min(SEUIL_MAX, seuil))

# ---------- Monte Carlo ----------
def monte_carlo_decision(seuil_candidate):
    total_gain = 0.0
    for _ in range(MONTE_CARLO_ITER):
        ventes = get_recent_ventes(20)
        if ventes:
            avg_montant = sum(v[0] for v in ventes) / len(ventes)
            prob_vendre = 1.0 / (seuil_candidate + 1)
            if random.random() < prob_vendre:
                total_gain += avg_montant
    return total_gain / MONTE_CARLO_ITER

# ---------- Décision avec epsilon ----------
def decide_seuil(mem):
    global EPSILON
    # Exploration aléatoire selon epsilon
    if random.random() < EPSILON:
        return random.randint(SEUIL_MIN, SEUIL_MAX)
    # Sinon exploitation : fusion des algorithmes
    seuil_pso = pso_optimize(iterations=15, swarm_size=10)
    seuil_gen = genetic_optimize()
    ventes = [v[0] for v in get_recent_ventes(30)]
    if len(ventes) > 5:
        pred = HoltWinters.predict(ventes, alpha=0.3, beta=0.1, steps=1)
        seuil_hw = max(SEUIL_MIN, min(SEUIL_MAX, int(SEUIL_MAX - pred * 10)))
    else:
        seuil_hw = 5
    pattern = mem.get("pattern_memory", [])
    if pattern:
        most_common = max(set(pattern), key=pattern.count)
        seuil_pattern = most_common
    else:
        seuil_pattern = 5
    seuil = int(0.4 * seuil_pso + 0.3 * seuil_gen + 0.2 * seuil_hw + 0.1 * seuil_pattern)
    seuil = max(SEUIL_MIN, min(SEUIL_MAX, seuil))
    gain_estime = monte_carlo_decision(seuil)
    mem["last_mc_gain"] = gain_estime
    return seuil

def update_memory(mem, seuil, reward):
    mem["historique"].append({"seuil": seuil, "reward": reward, "time": time.time()})
    if len(mem["historique"]) > 100:
        mem["historique"] = mem["historique"][-100:]
    if reward > 0:
        mem["pattern_memory"].append(seuil)
        if len(mem["pattern_memory"]) > 100:
            mem["pattern_memory"] = mem["pattern_memory"][-100:]
    if reward > mem["meilleur_score"]:
        mem["meilleur_score"] = reward
        mem["seuil"] = seuil
    else:
        mem["seuil"] = max(SEUIL_MIN, min(SEUIL_MAX, seuil + random.randint(-1, 1)))
    save_memory(mem)

def main():
    global EPSILON
    print(f"⚛️ Quantum ×100 avec epsilon = {EPSILON} démarré", flush=True)
    mem = load_memory()
    # Décroissance epsilon optionnelle (pour moins d'exploration avec le temps)
    # Pour l'instant, on le laisse fixe.
    while True:
        nb = get_unsold_count()
        seuil = decide_seuil(mem)
        if nb >= seuil:
            print(f"💡 Vente: {nb} emails (seuil={seuil}) | gain MC: {mem.get('last_mc_gain',0):.4f} | epsilon={EPSILON}", flush=True)
            subprocess.run(["python", os.path.expanduser("~/departement_ventes/sell_emails_paypal.py")])
            time.sleep(10)
            reward = get_recent_revenue(1)
            update_memory(mem, seuil, reward)
            print(f"📈 Récompense: {reward:.4f} USD", flush=True)
        else:
            print(f"⏳ Attente: {nb} emails < seuil {seuil}", flush=True)
        time.sleep(60)

if __name__ == "__main__":
    main()
