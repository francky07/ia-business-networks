#!/usr/bin/env python3
"""
CEO SUPER INTELLIGENT – 500 agents + 500 boosters
Avec mémoire, Q‑learning, prédiction et décisions adaptatives.
"""
import time, os, json, sqlite3, subprocess, traceback, random, requests, numpy as np
from datetime import datetime
from collections import deque
from web3 import Web3

DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
ENV_FILE = os.path.expanduser("~/.env_ia_business")
STATE_DIR = os.path.expanduser("~/ia_ceo_state")
os.makedirs(STATE_DIR, exist_ok=True)
LOG_FILE = os.path.join(STATE_DIR, "ceo_super_intelligent.log")
QTABLE_FILE = os.path.join(STATE_DIR, "q_table.json")

NB_AGENTS = 500
NB_BOOSTERS = 500
CYCLE_DECISION = 60      # secondes
CYCLE_RAPPORT = 3600

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def get_env(key, default=None):
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                if line.startswith("export "): line = line[7:]
                if "=" in line and line.split("=")[0].strip() == key:
                    return line.split("=",1)[1].strip().strip("\"'")
    return default

def get_bnb_usd_rate():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=usd", timeout=5)
        if r.status_code == 200:
            return float(r.json()["binancecoin"]["usd"])
    except: pass
    return 600.0

def get_bnb_balance():
    try:
        w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.binance.org"))
        address = "0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363"
        bal_wei = w3.eth.get_balance(address)
        return float(w3.from_wei(bal_wei, 'ether'))
    except Exception as e:
        log(f"Erreur BNB: {e}")
        return 0.0

def get_db_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM emails WHERE vendu=0")
        stock = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM leads")
        leads = c.fetchone()[0]
        conn.close()
        return stock, leads
    except:
        return 0, 0

def get_bot_count():
    out = subprocess.run(["tmux", "ls"], capture_output=True, text=True).stdout
    sessions = [l for l in out.splitlines() if "ceo_super" not in l and l]
    return len(sessions)

# ========== PRÉDICTION ==========
class Predictor:
    def __init__(self, window=24):
        self.revenue_history = deque(maxlen=window)
        self.stock_history = deque(maxlen=window)
    def update(self, revenue, stock):
        self.revenue_history.append(revenue)
        self.stock_history.append(stock)
    def predict_revenue(self):
        if len(self.revenue_history) < 3:
            return 0
        # moyenne mobile pondérée
        weights = [0.5, 0.3, 0.2]
        recent = list(self.revenue_history)[-3:]
        return sum(w * v for w, v in zip(weights, recent))
    def predict_stock(self):
        if len(self.stock_history) < 3:
            return 0
        return np.mean(list(self.stock_history)[-3:])

# ========== Q‑LEARNING (mémoire) ==========
class QLearning:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.q_table = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.load()
    def _state_key(self, stock_bin, revenue_bin, leads_bin, bots_bin):
        return (stock_bin, revenue_bin, leads_bin, bots_bin)
    def get_state(self, stock, revenue, leads, bots):
        # discrétisation
        s_bin = min(3, stock // 100)
        r_bin = min(2, int(revenue // 0.5))
        l_bin = min(2, leads // 25)
        b_bin = min(2, bots // 10)
        return self._state_key(s_bin, r_bin, l_bin, b_bin)
    def choose_action(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0.0, 0.0, 0.0, 0.0]  # 4 actions
        if random.random() < self.epsilon:
            return random.randint(0, 3)
        else:
            return np.argmax(self.q_table[state])
    def update(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = [0.0, 0.0, 0.0, 0.0]
        if next_state not in self.q_table:
            self.q_table[next_state] = [0.0, 0.0, 0.0, 0.0]
        old_value = self.q_table[state][action]
        next_max = np.max(self.q_table[next_state])
        new_value = old_value + self.alpha * (reward + self.gamma * next_max - old_value)
        self.q_table[state][action] = new_value
        self.save()
    def save(self):
        with open(QTABLE_FILE, "w") as f:
            json.dump({str(k): v for k, v in self.q_table.items()}, f)
    def load(self):
        if os.path.exists(QTABLE_FILE):
            with open(QTABLE_FILE) as f:
                data = json.load(f)
                self.q_table = {eval(k): v for k, v in data.items()}

# ========== AGENTS DÉCISIONNELS (500+500) ==========
class DecisionAgent:
    def __init__(self, agent_id, booster=False):
        self.id = agent_id
        self.booster = booster
        self.bias = random.uniform(-0.3, 0.3) if not booster else random.uniform(-0.5, 0.5)
        self.weight = 2.0 if booster else 1.0
    def vote(self, context):
        scores = [0.0, 0.0, 0.0, 0.0]
        stock = context.get("stock", 0)
        revenue = context.get("revenue", 0)
        leads = context.get("leads", 0)
        bots = context.get("bots", 0)
        pred = context.get("pred_revenue", 0)
        # Règles améliorées
        if stock > 50 and revenue < 1:
            scores[0] += 0.9
        if pred > 0.5 and stock > 20:
            scores[0] += 0.6
        if leads < 20:
            scores[1] += 0.7
        if bots < 12:
            scores[2] += 0.8
        if revenue > 3 and bots < 40:
            scores[3] += 0.7
        # Boosters plus agressifs
        if self.booster:
            for i in range(4):
                scores[i] *= 1.2
        for i in range(4):
            scores[i] += random.uniform(-0.1, 0.1) * self.bias
        return scores

class SwarmDecision:
    def __init__(self, n_agents=500, n_boosters=500):
        self.agents = [DecisionAgent(i, booster=False) for i in range(n_agents)]
        self.boosters = [DecisionAgent(i, booster=True) for i in range(n_boosters)]
        self.all_agents = self.agents + self.boosters
        self.weights = [1.0] * len(self.all_agents)
    def decide(self, context):
        votes = [0.0]*4
        for i, ag in enumerate(self.all_agents):
            scores = ag.vote(context)
            for a in range(4):
                votes[a] += scores[a] * self.weights[i] * ag.weight
        total = sum(votes)
        if total == 0: total = 1
        probs = [v/total for v in votes]
        action = random.choices(range(4), weights=probs, k=1)[0]
        return action, probs
    def reward(self, action, reward, context):
        for i, ag in enumerate(self.all_agents):
            scores = ag.vote(context)
            if scores[action] > 0.2:
                self.weights[i] += 0.005 * max(0, reward)
        total = sum(self.weights)
        if total > 0:
            self.weights = [w/total for w in self.weights]

# ========== VISION, OBJECTIFS, RH, FINANCE ==========
class Vision:
    def __init__(self):
        self.file = os.path.join(STATE_DIR, "vision.json")
        self.load()
    def load(self):
        if os.path.exists(self.file):
            with open(self.file) as f:
                data = json.load(f)
                self.mission = data.get("mission", "Devenir le leader mondial de l'automatisation IA.")
                self.values = data.get("values", ["Innovation", "Autonomie", "Rentabilité", "Audace"])
        else:
            self.mission = "Devenir le leader mondial de l'automatisation IA."
            self.values = ["Innovation", "Autonomie", "Rentabilité", "Audace"]
            self.save()
    def save(self):
        with open(self.file, "w") as f:
            json.dump({"mission": self.mission, "values": self.values}, f, indent=2)
    def report(self):
        return f"Mission: {self.mission}\nValeurs: {', '.join(self.values)}"

class Objectives:
    def __init__(self):
        self.file = os.path.join(STATE_DIR, "objectives.json")
        self.load()
    def load(self):
        if os.path.exists(self.file):
            with open(self.file) as f:
                self.data = json.load(f)
        else:
            self.data = {
                "short_term": {"revenue_target": 10.0, "stock_target": 100, "leads_target": 50},
                "medium_term": {"revenue_target": 100.0, "market_share": 0.02},
                "long_term": {"revenue_target": 1000.0, "bots_count": 50}
            }
            self.save()
    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f, indent=2)
    def update(self, real_revenue, stock, leads, bots):
        if real_revenue > self.data["short_term"]["revenue_target"] * 0.8:
            self.data["short_term"]["revenue_target"] *= 1.1
            log(f"Objectif court terme augmenté à {self.data['short_term']['revenue_target']:.2f} USD")
        elif real_revenue < self.data["short_term"]["revenue_target"] * 0.3:
            self.data["short_term"]["revenue_target"] *= 0.9
            log(f"Objectif court terme réduit à {self.data['short_term']['revenue_target']:.2f} USD")
        if stock > self.data["short_term"]["stock_target"] * 1.2:
            self.data["short_term"]["stock_target"] = int(stock * 0.8)
            log(f"Objectif stock ajusté à {self.data['short_term']['stock_target']}")
        self.save()
    def report(self):
        return f"Court: {self.data['short_term']}\nMoyen: {self.data['medium_term']}\nLong: {self.data['long_term']}"

class HR:
    def __init__(self):
        self.file = os.path.join(STATE_DIR, "hr.json")
        self.load()
    def load(self):
        if os.path.exists(self.file):
            with open(self.file) as f:
                self.data = json.load(f)
        else:
            self.data = {"agents": {}, "recruitment_history": []}
            self.save()
    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f, indent=2)
    def evaluate_agents(self):
        out = subprocess.run(["tmux", "ls"], capture_output=True, text=True).stdout
        active = [line.split(":")[0] for line in out.splitlines() if "ceo_super" not in line and line]
        for a in active:
            if a not in self.data["agents"]:
                self.data["agents"][a] = {"productivity": 0.5, "last_seen": time.time()}
            else:
                self.data["agents"][a]["last_seen"] = time.time()
                self.data["agents"][a]["productivity"] = min(1.0, self.data["agents"][a]["productivity"] + 0.01)
        now = time.time()
        to_remove = [a for a, info in self.data["agents"].items() if now - info["last_seen"] > 3600]
        for a in to_remove:
            del self.data["agents"][a]
            log(f"RH: Agent {a} supprimé")
        self.save()
        return len(self.data["agents"])
    def recruit(self, bot_type="booster"):
        log(f"RH: Recrutement d'un {bot_type}")
        if bot_type == "booster":
            subprocess.run(["tmux", "new-session", "-d", "-s", f"recruit_{int(time.time())}", "python ~/ia_booster_agence.py"], shell=True)
        else:
            subprocess.run(["tmux", "new-session", "-d", "-s", f"recruit_{int(time.time())}", "python ~/ia_net_pro.py"], shell=True)
        self.data["recruitment_history"].append({"time": time.time(), "type": bot_type})
        self.save()
    def report(self):
        nb = len(self.data["agents"])
        avg = sum(a["productivity"] for a in self.data["agents"].values()) / nb if nb else 0
        return f"Agents actifs: {nb}, Prod moy: {avg:.2f}"

class Finance:
    def __init__(self):
        self.cash = 0.0
        self.history = deque(maxlen=100)
    def update(self, bnb_usd):
        self.cash = bnb_usd
        self.history.append({"time": time.time(), "cash": self.cash})
    def get_trend(self):
        if len(self.history) < 2: return "stable"
        last = self.history[-1]["cash"]
        prev = self.history[-2]["cash"]
        if last > prev * 1.05: return "hausse"
        if last < prev * 0.95: return "baisse"
        return "stable"
    def report(self):
        return f"Trésorerie: {self.cash:.2f} USD | Tendance: {self.get_trend()}"

# ========== BOUCLE PRINCIPALE ==========
def main():
    log(f"🧠 CEO SUPER INTELLIGENT – {NB_AGENTS} agents + {NB_BOOSTERS} boosters", "START")
    vision = Vision()
    objectives = Objectives()
    hr = HR()
    finance = Finance()
    swarm = SwarmDecision(NB_AGENTS, NB_BOOSTERS)
    ql = QLearning()
    predictor = Predictor()
    cycle = 0
    last_action = 0
    last_report = 0
    last_reward = 0.0
    last_state = None
    last_action_taken = None

    while True:
        try:
            cycle += 1
            # Collecte
            bnb = get_bnb_balance()
            rate = get_bnb_usd_rate()
            bnb_usd = bnb * rate
            stock, leads = get_db_stats()
            bots = get_bot_count()
            finance.update(bnb_usd)
            objectives.update(bnb_usd, stock, leads, bots)
            hr.evaluate_agents()
            predictor.update(bnb_usd, stock)
            pred_rev = predictor.predict_revenue()
            # Contexte enrichi
            context = {
                "stock": stock,
                "revenue": bnb_usd,
                "leads": leads,
                "bots": bots,
                "pred_revenue": pred_rev
            }
            # État pour Q-learning
            state = ql.get_state(stock, bnb_usd, leads, bots)
            now = time.time()
            if now - last_action >= CYCLE_DECISION:
                # Choix de l'action par Q-learning et swarm (combinaison)
                q_action = ql.choose_action(state)
                swarm_action, probs = swarm.decide(context)
                # Fusion (poids 0.6 pour swarm, 0.4 pour Q-learning)
                combined = [0.6 * probs[i] + 0.4 * (1 if i == q_action else 0) for i in range(4)]
                total = sum(combined)
                probs_final = [p/total for p in combined]
                action = random.choices(range(4), weights=probs_final, k=1)[0]
                # Exécution
                if action == 0 and stock > 5:
                    log("ACTION: Vente massive", "ACTION")
                    subprocess.run(["python", os.path.expanduser("~/departement_ventes/sell_emails_paypal.py")])
                elif action == 1:
                    log("ACTION: Campagne marketing (simulation)", "ACTION")
                elif action == 2:
                    log("ACTION: Recrutement d'un booster", "ACTION")
                    hr.recruit("booster")
                elif action == 3 and bnb_usd > 5:
                    log("ACTION: Investissement (simulation)", "ACTION")
                # Récompense
                reward = bnb_usd - last_reward
                # Mise à jour Q-learning
                next_state = ql.get_state(stock, bnb_usd, leads, bots)
                ql.update(state, action, reward, next_state)
                # Récompense du swarm
                swarm.reward(action, reward, context)
                last_reward = bnb_usd
                last_action = now
                last_state = state
                last_action_taken = action
            # Rapport horaire
            if now - last_report >= CYCLE_RAPPORT:
                report = (
                    f"📊 RAPPORT CEO SUPER INTELLIGENT - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                    f"💰 BNB: {bnb_usd:.2f} USD (taux {rate:.2f})\n"
                    f"📧 Stock: {stock}\n👥 Leads: {leads}\n🤖 Bots: {bots}\n"
                    f"🔮 Prédiction revenu: {pred_rev:.2f} USD\n"
                    f"🎯 {objectives.report()}\n"
                    f"🧠 {vision.report()}\n"
                    f"👥 {hr.report()}\n"
                    f"💵 {finance.report()}"
                )
                log(report, "REPORT")
                last_report = now
            if cycle % 10 == 0:
                log(f"Cycle {cycle}: BNB={bnb_usd:.2f} USD, Stock={stock}, Leads={leads}, Bots={bots}")
            time.sleep(60)
        except Exception as e:
            log(f"Erreur fatale: {e}\n{traceback.format_exc()}", "ERROR")
            time.sleep(60)

if __name__ == "__main__":
    main()
