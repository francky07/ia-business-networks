#!/usr/bin/env python3
"""
Module d'intelligence quantique – Superposition, interférence, optimisation
"""
import sqlite3
import numpy as np
import random
import json
import os
import time
from collections import defaultdict

DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
MEM_PATH = os.path.expanduser("~/ia_nexus/quantum/quantum_memory.json")

class Qubit:
    """Simulation d'un qubit (état superposé)"""
    def __init__(self, alpha=1.0, beta=0.0):
        norm = np.sqrt(alpha**2 + beta**2)
        self.alpha = alpha / norm if norm != 0 else 1.0
        self.beta = beta / norm if norm != 0 else 0.0

    def measure(self):
        """Mesure probabiliste -> 0 ou 1"""
        prob1 = self.beta**2
        return 1 if random.random() < prob1 else 0

    def apply_gate(self, gate_matrix):
        new_alpha = gate_matrix[0][0]*self.alpha + gate_matrix[0][1]*self.beta
        new_beta  = gate_matrix[1][0]*self.alpha + gate_matrix[1][1]*self.beta
        norm = np.sqrt(new_alpha**2 + new_beta**2)
        self.alpha = new_alpha / norm
        self.beta = new_beta / norm

class QuantumBrain:
    def __init__(self):
        self.qubits = {}
        self.memory = self.load_memory()
        self.annealing_temp = 1.0
        self.best_solution = None
        self.best_score = -float('inf')

    def load_memory(self):
        if os.path.exists(MEM_PATH):
            with open(MEM_PATH) as f:
                return json.load(f)
        return {"strategy_weights": [0.5,0.5,0.5], "last_actions": []}

    def save_memory(self):
        with open(MEM_PATH, 'w') as f:
            json.dump(self.memory, f)

    def get_state_vector(self):
        """État du système (stock, ventes, heure) -> vecteur quantique"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM emails WHERE vendu=0")
        stock = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(montant),0) FROM ventes WHERE date > strftime('%s','now','-1 hour')")
        recent_rev = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(montant),0) FROM ventes WHERE date > strftime('%s','now','-1 day')")
        daily_rev = c.fetchone()[0]
        conn.close()
        # Normalisation
        stock_norm = min(1.0, stock / 1000)
        rev_norm = min(1.0, recent_rev / 1.0)
        daily_norm = min(1.0, daily_rev / 10.0)
        hour = time.localtime().tm_hour
        hour_norm = hour / 24.0
        return np.array([stock_norm, rev_norm, daily_norm, hour_norm])

    def quantum_superposition(self, state):
        """Génère plusieurs stratégies en superposition (probabilités)"""
        strategies = []
        # Stratégie 1 : agressif (vendre même peu)
        # Stratégie 2 : modéré (vendre à seuil moyen)
        # Stratégie 3 : patient (vendre à seuil élevé)
        # Les poids dépendent de l'état quantique
        weights = self.memory["strategy_weights"]
        # Appliquer des portes quantiques (rotation)
        phase = np.sin(state[0] * np.pi)  # interférence
        w1 = max(0, weights[0] + 0.1*phase)
        w2 = max(0, weights[1] - 0.05*phase)
        w3 = max(0, weights[2] + 0.05*np.cos(state[1]*np.pi))
        total = w1+w2+w3
        if total == 0: total = 1
        probs = [w1/total, w2/total, w3/total]
        return probs

    def simulated_annealing_decision(self):
        """Recuit simulé pour trouver le meilleur seuil"""
        current_seuil = random.randint(1, 20)
        current_score = self.evaluate_seuil(current_seuil)
        temp = self.annealing_temp
        for _ in range(50):
            new_seuil = max(1, current_seuil + random.randint(-3, 3))
            new_score = self.evaluate_seuil(new_seuil)
            if new_score > current_score or random.random() < np.exp((new_score - current_score)/temp):
                current_seuil = new_seuil
                current_score = new_score
            temp *= 0.95
        self.annealing_temp = max(0.1, self.annealing_temp * 0.99)
        return current_seuil

    def evaluate_seuil(self, seuil):
        """Score virtuel d'un seuil (basé sur historique)"""
        # Idée : un seuil bas vend plus mais peut-être trop tôt
        # Simulé à partir des données de ventes passées
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT AVG(montant), COUNT(*) FROM ventes WHERE date > strftime('%s','now','-7 day')")
        avg, nb = c.fetchone()
        conn.close()
        if nb == 0:
            return 0
        # Score : plus le seuil est bas, plus on vend souvent, mais on veut maximiser revenu
        # Formule heuristique
        score = (avg / (seuil + 1)) * nb
        return score

    def neural_network_predict(self, state):
        """Petit réseau de neurones (2 couches) pour prédire le meilleur seuil"""
        # Poids aléatoires stockés dans mémoire
        if "nn_weights" not in self.memory:
            self.memory["nn_weights"] = np.random.randn(4, 3).tolist()
        weights = np.array(self.memory["nn_weights"])
        hidden = np.tanh(np.dot(state, weights))
        output = np.tanh(np.dot(hidden, np.array([1.0, -0.5, 0.2])))  # couche de sortie
        seuil = int(abs(output[0]) * 20) + 1
        return max(1, min(20, seuil))

    def decide(self):
        """Prise de décision quantique"""
        state = self.get_state_vector()
        # Superposition de stratégies
        probs = self.quantum_superposition(state)
        strategy = np.random.choice([0,1,2], p=probs)
        if strategy == 0:
            seuil = self.simulated_annealing_decision()
        elif strategy == 1:
            seuil = max(1, int(state[0]*50) + 5)
        else:
            seuil = self.neural_network_predict(state)
        # Mémoriser l'action
        self.memory["last_actions"].append((time.time(), seuil, state.tolist()))
        if len(self.memory["last_actions"]) > 100:
            self.memory["last_actions"] = self.memory["last_actions"][-100:]
        self.save_memory()
        return seuil

    def reward(self, gain):
        """Renforcement : ajuste les poids des stratégies"""
        # Gain positif -> renforcer la stratégie utilisée
        if gain > 0:
            self.memory["strategy_weights"] = [w + 0.01 for w in self.memory["strategy_weights"]]
            total = sum(self.memory["strategy_weights"])
            self.memory["strategy_weights"] = [w/total for w in self.memory["strategy_weights"]]
        else:
            # Pénaliser légèrement
            self.memory["strategy_weights"] = [w - 0.005 for w in self.memory["strategy_weights"]]
            self.memory["strategy_weights"] = [max(0.1, w) for w in self.memory["strategy_weights"]]
        self.save_memory()

quantum_brain = QuantumBrain()
