#!/usr/bin/env python3
import time, os, json, random, math, sqlite3
from datetime import datetime

DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
STATE_DIR = os.path.expanduser("~/ia_ceo_state")
os.makedirs(STATE_DIR, exist_ok=True)
BOOST_FILE = os.path.join(STATE_DIR, "neuronal_boost.json")
LOG_FILE = os.path.join(STATE_DIR, "neuronal_booster.log")

def log(msg):
    print(f"[{datetime.now()}] {msg}")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

class NeuralBooster:
    def __init__(self):
        self.w1 = [[random.uniform(-0.5,0.5) for _ in range(8)] for __ in range(4)]
        self.b1 = [0.0]*8
        self.w2 = [[random.uniform(-0.5,0.5) for _ in range(5)] for __ in range(8)]
        self.b2 = [0.0]*5
        self.lr = 0.01
        self.load()
    def sigmoid(self, x):
        return 1/(1+math.exp(-x))
    def forward(self, x):
        h = [self.sigmoid(sum(x[i]*self.w1[i][j] for i in range(4)) + self.b1[j]) for j in range(8)]
        out = [self.sigmoid(sum(h[j]*self.w2[j][k] for j in range(8)) + self.b2[k]) for k in range(5)]
        return out
    def predict_action(self, state):
        probs = self.forward(state)
        return probs.index(max(probs)), probs
    def train(self, state, target_action, reward):
        probs = self.forward(state)
        error = [0.0]*5
        for i in range(5):
            error[i] = (1 if i==target_action else 0) - probs[i]
        for j in range(8):
            for k in range(5):
                self.w2[j][k] += self.lr * error[k] * probs[k]*(1-probs[k]) * self.sigmoid(sum(state[i]*self.w1[i][j] for i in range(4)) + self.b1[j])
        for k in range(5):
            self.b2[k] += self.lr * error[k] * probs[k]*(1-probs[k])
        self.save()
    def save(self):
        with open(os.path.join(STATE_DIR, "neuronal_weights.json"), "w") as f:
            json.dump({"w1": self.w1, "b1": self.b1, "w2": self.w2, "b2": self.b2}, f)
    def load(self):
        fpath = os.path.join(STATE_DIR, "neuronal_weights.json")
        if os.path.exists(fpath):
            with open(fpath) as f:
                data = json.load(f)
                self.w1 = data["w1"]
                self.b1 = data["b1"]
                self.w2 = data["w2"]
                self.b2 = data["b2"]

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
    import subprocess
    out = subprocess.run(["tmux", "ls"], capture_output=True, text=True).stdout
    return len([l for l in out.splitlines() if "ceo_neuronal" not in l and l])

def main():
    log("Booster neuronal démarré")
    nn = NeuralBooster()
    while True:
        try:
            stock, leads = get_db_stats()
            bots = get_bot_count()
            revenue = stock * 0.01
            state = [min(1, stock/200), min(1, revenue/5), min(1, leads/50), min(1, bots/30)]
            action, probs = nn.predict_action(state)
            with open(BOOST_FILE, "w") as f:
                json.dump({"timestamp": time.time(), "action": action, "probs": probs, "state": state}, f)
            log(f"Suggestion action {action}")
            time.sleep(60)
        except Exception as e:
            log(f"Erreur: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
