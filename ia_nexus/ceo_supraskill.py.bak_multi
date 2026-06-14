#!/usr/bin/env python3
"""
CEO SUPRASKILL – Compétences suprêmes : Deep Q‑Learning, agents spécialisés, mémoire, prédiction avancée.
"""
import time, os, json, sqlite3, subprocess, traceback, random, requests, math
from datetime import datetime
from collections import deque
from web3 import Web3

# ==================== CONFIGURATION ====================
DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
ENV_FILE = os.path.expanduser("~/.env_ia_business")
STATE_DIR = os.path.expanduser("~/ia_ceo_state")
os.makedirs(STATE_DIR, exist_ok=True)
LOG_FILE = os.path.join(STATE_DIR, "ceo_supraskill.log")
MEMORY_FILE = os.path.join(STATE_DIR, "episodic_memory.json")
DQN_FILE = os.path.join(STATE_DIR, "dqn_weights.json")

NB_AGENTS = 800
NB_BOOSTERS = 800
CYCLE_DECISION = 45      # secondes
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

# ==================== PORTEFEUILLES ====================
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
    sessions = [l for l in out.splitlines() if "ceo_supraskill" not in l and l]
    return len(sessions)

# ==================== MÉMOIRE ÉPISODIQUE ====================
class EpisodicMemory:
    def __init__(self, capacity=200):
        self.memory = deque(maxlen=capacity)
        self.load()
    def add(self, episode):
        self.memory.append(episode)
        self.save()
    def get_similar(self, state, k=3):
        similarities = []
        for ep in self.memory:
            if "state" in ep:
                score = sum(a*b for a,b in zip(state, ep["state"])) / (math.sqrt(sum(s*s for s in state)) * math.sqrt(sum(s*s for s in ep["state"])) + 1e-9)
                similarities.append((score, ep))
        similarities.sort(reverse=True)
        return [ep for _, ep in similarities[:k]]
    def save(self):
        with open(MEMORY_FILE, "w") as f:
            json.dump(list(self.memory), f, indent=2)
    def load(self):
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE) as f:
                data = json.load(f)
                self.memory = deque(data, maxlen=200)

# ==================== DEEP Q-NETWORK (simulé) ====================
class DeepQNetwork:
    def __init__(self, state_dim=5, action_dim=4, lr=0.01, gamma=0.95, epsilon=0.2):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.weights = {}
        self.load()
    def _init_weights(self):
        self.weights = {
            "w1": [[random.uniform(-0.1,0.1) for _ in range(16)] for __ in range(self.state_dim)],
            "b1": [0.0]*16,
            "w2": [[random.uniform(-0.1,0.1) for _ in range(self.action_dim)] for __ in range(16)],
            "b2": [0.0]*self.action_dim
        }
    def forward(self, state):
        h = [sum(state[i]*self.weights["w1"][i][j] for i in range(self.state_dim)) + self.weights["b1"][j] for j in range(16)]
        h = [max(0, x) for x in h]
        out = [sum(h[j]*self.weights["w2"][j][a] for j in range(16)) + self.weights["b2"][a] for a in range(self.action_dim)]
        return out
    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.action_dim-1)
        qvals = self.forward(state)
        return qvals.index(max(qvals))
    def update(self, state, action, reward, next_state, done=False):
        q = self.forward(state)[action]
        if done:
            target = reward
        else:
            next_q = max(self.forward(next_state))
            target = reward + self.gamma * next_q
        error = target - q
        for i in range(self.state_dim):
            self.weights["w1"][i][0] += self.lr * error * state[i]
        self.weights["b1"][0] += self.lr * error
        self.save()
    def save(self):
        with open(DQN_FILE, "w") as f:
            json.dump(self.weights, f)
    def load(self):
        if os.path.exists(DQN_FILE):
            with open(DQN_FILE) as f:
                self.weights = json.load(f)
        else:
            self._init_weights()

# ==================== AGENTS SPÉCIALISÉS ====================
class SpecialistAgent:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.confidence = 0.5
        self.history = deque(maxlen=50)
    def advise(self, context):
        stock = context.get("stock", 0)
        revenue = context.get("revenue", 0)
        leads = context.get("leads", 0)
        bots = context.get("bots", 0)
        if self.role == "sales":
            if stock > 50 and revenue < 1:
                return 0, 0.9
        elif self.role == "marketing":
            if leads < 20:
                return 1, 0.7
        elif self.role == "hr":
            if bots < 10:
                return 2, 0.8
        elif self.role == "finance":
            if revenue > 5 and bots < 40:
                return 3, 0.6
        return None, 0.0

# ==================== AGENTS DÉCISIONNELS (800+800) ====================
class DecisionAgent:
    def __init__(self, agent_id, booster=False):
        self.id = agent_id
        self.booster = booster
        self.bias = random.uniform(-0.3, 0.3)
        self.weight = 2.0 if booster else 1.0
    def vote(self, context):
        scores = [0.0,0.0,0.0,0.0]
        stock = context.get("stock",0)
        revenue = context.get("revenue",0)
        leads = context.get("leads",0)
        bots = context.get("bots",0)
        pred = context.get("pred_revenue",0)
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
        if self.booster:
            for i in range(4): scores[i] *= 1.2
        for i in range(4):
            scores[i] += random.uniform(-0.1,0.1)*self.bias
        return scores

class SwarmDecision:
    def __init__(self, n_agents=800, n_boosters=800):
        self.agents = [DecisionAgent(i, booster=False) for i in range(n_agents)]
        self.boosters = [DecisionAgent(i, booster=True) for i in range(n_boosters)]
        self.all_agents = self.agents + self.boosters
        self.weights = [1.0]*len(self.all_agents)
    def decide(self, context):
        votes = [0.0]*4
        for i, ag in enumerate(self.all_agents):
            scores = ag.vote(context)
            for a in range(4):
                votes[a] += scores[a]*self.weights[i]*ag.weight
        total = sum(votes)
        if total==0: total=1
        probs = [v/total for v in votes]
        action = random.choices(range(4), weights=probs, k=1)[0]
        return action, probs
    def reward(self, action, reward, context):
        for i, ag in enumerate(self.all_agents):
            scores = ag.vote(context)
            if scores[action] > 0.2:
                self.weights[i] += 0.005*max(0, reward)
        total = sum(self.weights)
        if total>0: self.weights = [w/total for w in self.weights]

# ==================== VISION, OBJECTIFS, RH, FINANCE ====================
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
        active = [line.split(":")[0] for line in out.splitlines() if "ceo_supraskill" not in line and line]
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

# ==================== PRÉDICTION AVANCÉE ====================
class Predictor:
    def __init__(self, window=24):
        self.revenue_history = deque(maxlen=window)
        self.stock_history = deque(maxlen=window)
    def update(self, revenue, stock):
        self.revenue_history.append(revenue)
        self.stock_history.append(stock)
    def predict_revenue(self):
        if len(self.revenue_history) < 3: return 0
        weights = [0.5,0.3,0.2]
        recent = list(self.revenue_history)[-3:]
        return sum(w*v for w,v in zip(weights, recent))
    def predict_stock(self):
        if len(self.stock_history) < 3: return 0
        return sum(list(self.stock_history)[-3:])/3

# ==================== DÉTECTION D'ANOMALIES ====================
class AnomalyDetector:
    def __init__(self):
        self.revenue_std = None
        self.stock_std = None
    def update(self, revenue, stock):
        pass
    def is_anomaly(self, revenue, stock):
        return revenue < 0.1 and stock > 200

# ==================== BOUCLE PRINCIPALE ====================
def main():
    log(f"🧠 CEO SUPRASKILL – {NB_AGENTS} agents + {NB_BOOSTERS} boosters", "START")
    vision = Vision()
    objectives = Objectives()
    hr = HR()
    finance = Finance()
    swarm = SwarmDecision(NB_AGENTS, NB_BOOSTERS)
    dqn = DeepQNetwork(state_dim=5, action_dim=4)
    memory = EpisodicMemory()
    predictor = Predictor()
    anomaly = AnomalyDetector()
    specialists = [SpecialistAgent("Sales","sales"), SpecialistAgent("Marketing","marketing"),
                   SpecialistAgent("HR","hr"), SpecialistAgent("Finance","finance")]
    cycle = 0
    last_action = 0
    last_report = 0
    last_reward = 0.0

    while True:
        try:
            cycle += 1
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
            anomaly_detected = anomaly.is_anomaly(bnb_usd, stock)
            state_vec = [min(1, stock/500), min(1, bnb_usd/10), min(1, leads/100), min(1, bots/50), float(anomaly_detected)]
            context = {"stock": stock, "revenue": bnb_usd, "leads": leads, "bots": bots, "pred_revenue": pred_rev}
            now = time.time()
            if now - last_action >= CYCLE_DECISION:
                # Recuperer conseils des spécialistes
                advices = {}
                for s in specialists:
                    act, conf = s.advise(context)
                    if act is not None:
                        advices[act] = advices.get(act,0) + conf
                # Décision finale
                dqn_action = dqn.choose_action(state_vec)
                swarm_action, swarm_probs = swarm.decide(context)
                # Pondération : 0.5 swarm, 0.3 dqn, 0.2 spécialistes
                combined = [0.5*swarm_probs[i] + 0.3*(1 if i==dqn_action else 0) + 0.2*advices.get(i,0) for i in range(4)]
                total = sum(combined)
                if total==0: total=1
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
                # Récompense et apprentissage
                reward = bnb_usd - last_reward
                next_state = [min(1, stock/500), min(1, bnb_usd/10), min(1, leads/100), min(1, bots/50), float(anomaly_detected)]
                dqn.update(state_vec, action, reward, next_state)
                swarm.reward(action, reward, context)
                memory.add({"state": state_vec, "action": action, "reward": reward})
                last_reward = bnb_usd
                last_action = now
            # Rapport horaire
            if now - last_report >= CYCLE_RAPPORT:
                report = (
                    f"📊 RAPPORT CEO SUPRASKILL - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                    f"💰 BNB: {bnb_usd:.2f} USD (taux {rate:.2f})\n"
                    f"📧 Stock: {stock}\n👥 Leads: {leads}\n🤖 Bots: {bots}\n"
                    f"🔮 Prédiction revenu: {pred_rev:.2f} USD\n"
                    f"⚠️ Anomalie: {anomaly_detected}\n"
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
