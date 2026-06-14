#!/usr/bin/env python3
import time, os, json, sqlite3, subprocess, requests, smtplib, ssl, glob, shutil, random, math
from datetime import datetime
from email.mime.text import MIMEText
from web3 import Web3

DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
LOG_FILE = os.path.expanduser("~/ceo_unified.log")
STATE_FILE = os.path.expanduser("~/ceo_unified_state.json")
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USER = "seckndananeuh@gmail.com"
SMTP_PASSWORD = "xsmtpsib-9364b75a7aa91f2040c5ccc04b90c01224b070f1efc4b97d5c21a896ec6e8527-BheO7lIdmm52XdF4"
PAYPAL_EMAIL = "faraseck@hotmail.fr"
NB_AGENTS = 800
NB_BOOSTERS = 800

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] [{level}] {msg}\n")

def get_env(key, default=None):
    env_file = os.path.expanduser("~/.env_ia_business")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith("export "): line = line[7:]
                if "=" in line and line.split("=")[0].strip() == key:
                    return line.split("=",1)[1].strip().strip("\"'")
    return default

def send_telegram(msg):
    token = get_env("TELEGRAM_BOT_TOKEN")
    chat_id = get_env("TELEGRAM_CHAT_ID")
    if token and chat_id and token != "VOTRE_TOKEN":
        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

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
        log(f"Erreur BNB: {e}", "ERROR")
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
    sessions = [l for l in out.splitlines() if "ceo_unified" not in l and l]
    return len(sessions)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"seuil_vente": 10, "prix_email": 0.01, "objectif_revenu": 10.0, "derniere_action": ""}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def action_vendre():
    subprocess.run(["python", os.path.expanduser("~/departement_ventes/sell_emails_paypal.py")])

def action_recruter():
    subprocess.run(["tmux", "new-session", "-d", "-s", f"recruit_{int(time.time())}", "python ~/ia_booster_agence.py"], shell=True)

def action_prix(up=True):
    state = load_state()
    if up:
        new_price = round(state.get("prix_email", 0.01) + 0.005, 3)
    else:
        new_price = max(0.002, state.get("prix_email", 0.01) - 0.005)
    state["prix_email"] = new_price
    save_state(state)
    subprocess.run(f"sed -i 's/montant = nb \\* [0-9.]*/montant = nb * {new_price}/' ~/departement_ventes/sell_emails_paypal.py", shell=True)

def action_investir():
    for _ in range(2):
        subprocess.run(["tmux", "new-session", "-d", "-s", f"invest_{int(time.time())}", "python ~/ia_booster_agence.py"], shell=True)

class DecisionAgent:
    def __init__(self, agent_id, booster=False):
        self.id = agent_id
        self.booster = booster
        self.bias = random.uniform(-0.3, 0.3)
        self.weight = 2.0 if booster else 1.0
    def vote(self, context):
        scores = [0.0, 0.0, 0.0, 0.0, 0.0]  # 0=vendre, 1=recruter, 2=prix-, 3=prix+, 4=investir
        stock = context.get("stock",0)
        revenue = context.get("revenue",0)
        bots = context.get("bots",0)
        if stock > 50 and revenue < 1: scores[0] += 0.9
        if bots < 12: scores[1] += 0.9
        if stock > 500: scores[2] += 0.7
        elif stock < 50 and revenue > 1: scores[3] += 0.6
        if revenue > 5 and bots < 40: scores[4] += 0.7
        if self.booster:
            for i in range(5): scores[i] *= 1.2
        for i in range(5):
            scores[i] += random.uniform(-0.1,0.1)*self.bias
        return scores

class SwarmDecision:
    def __init__(self, n_agents=800, n_boosters=800):
        self.agents = [DecisionAgent(i, booster=False) for i in range(n_agents)]
        self.boosters = [DecisionAgent(i, booster=True) for i in range(n_boosters)]
        self.all_agents = self.agents + self.boosters
        self.weights = [1.0]*len(self.all_agents)
    def decide(self, context):
        votes = [0.0]*5
        for i, ag in enumerate(self.all_agents):
            scores = ag.vote(context)
            for a in range(5):
                votes[a] += scores[a] * self.weights[i] * ag.weight
        total = sum(votes)
        if total==0: total=1
        probs = [v/total for v in votes]
        action = random.choices(range(5), weights=probs, k=1)[0]
        return action, probs
    def reward(self, action, reward, context):
        for i, ag in enumerate(self.all_agents):
            scores = ag.vote(context)
            if scores[action] > 0.2:
                self.weights[i] += 0.005 * max(0, reward)
        total = sum(self.weights)
        if total>0: self.weights = [w/total for w in self.weights]

def optimiser_base_sqlite():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("VACUUM")
        conn.execute("REINDEX")
        conn.close()
        log("Base SQLite optimisée", "SYSTEM")
    except: pass

def nettoyer_logs_anciens(days=7):
    log_files = glob.glob(os.path.expanduser("~/ia_ceo_state/*.log")) + glob.glob(os.path.expanduser("~/ceo_*.log"))
    deleted = 0
    for f in log_files:
        if os.path.isfile(f) and time.time() - os.path.getmtime(f) > days*86400:
            os.remove(f); deleted+=1
    log(f"{deleted} logs supprimés", "SYSTEM")

def surveiller_ressources():
    try:
        load = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
        with open("/proc/meminfo") as f: meminfo = f.read()
        mem_total = int([l for l in meminfo.splitlines() if "MemTotal" in l][0].split()[1])
        mem_avail = int([l for l in meminfo.splitlines() if "MemAvailable" in l][0].split()[1])
        mem_usage = (mem_total - mem_avail) / mem_total * 100
        disk = shutil.disk_usage("/")
        disk_usage = (disk.used / disk.total) * 100
        if load > 2.0 or mem_usage > 80 or disk_usage > 85:
            send_telegram(f"⚠️ Ressources élevées : CPU load={load:.2f}, Mémoire={mem_usage:.1f}%, Disque={disk_usage:.1f}%")
    except: pass

def redemarrer_bot_dead(bot_name):
    out = subprocess.run(["tmux", "ls"], capture_output=True, text=True).stdout
    if bot_name not in out:
        log(f"Bot {bot_name} redémarré", "SYSTEM")
        if bot_name == "agence_kays":
            subprocess.run(["tmux", "new-session", "-d", "-s", "agence_kays", "python ~/agence_kays/agence.py"], shell=True)
        elif bot_name == "ventes":
            subprocess.run(["tmux", "new-session", "-d", "-s", "ventes", "cd ~/departement_ventes && python ventes.py"], shell=True)
        elif bot_name == "ia_net":
            subprocess.run(["tmux", "new-session", "-d", "-s", "ia_net", "python ~/ia_net_pro.py"], shell=True)

def main():
    log("CEO UNIFIED démarré", "START")
    state = load_state()
    swarm = SwarmDecision(NB_AGENTS, NB_BOOSTERS)
    last_action = 0
    last_optim = 0
    last_clean = 0
    last_health = 0
    last_report = 0
    last_reward = 0.0

    while True:
        try:
            now = time.time()
            bnb = get_bnb_balance()
            rate = get_bnb_usd_rate()
            bnb_usd = bnb * rate
            stock, leads = get_db_stats()
            bots = get_bot_count()
            context = {"stock": stock, "revenue": bnb_usd, "leads": leads, "bots": bots}

            if now - last_action >= 60:
                action, probs = swarm.decide(context)
                # Lecture suggestion booster
                boost_file = os.path.expanduser("~/ia_ceo_state/neuronal_boost.json")
                if os.path.exists(boost_file):
                    try:
                        with open(boost_file) as bf:
                            boost_data = json.load(bf)
                            boost_action = boost_data.get("action")
                            if boost_action is not None:
                                probs[boost_action] += 0.2
                                total = sum(probs)
                                if total>0: probs = [p/total for p in probs]
                    except: pass
                action = random.choices(range(5), weights=probs, k=1)[0]
                log(f"Décision: action {action}", "ACTION")
                if action == 0 and stock > 5:
                    action_vendre()
                elif action == 1:
                    action_recruter()
                elif action == 2:
                    action_prix(up=False)
                elif action == 3:
                    action_prix(up=True)
                elif action == 4 and bnb_usd > 5:
                    action_investir()
                reward = bnb_usd - last_reward
                swarm.reward(action, reward, context)
                last_reward = bnb_usd
                state["derniere_action"] = str(action)
                save_state(state)
                last_action = now

            # Tâches périodiques
            if now - last_optim > 21600: optimiser_base_sqlite(); last_optim=now
            if now - last_clean > 86400: nettoyer_logs_anciens(); last_clean=now
            if now - last_health > 300: surveiller_ressources(); last_health=now
            if now - last_report > 3600:
                send_telegram(f"📊 RAPPORT - {datetime.now()}\n💰 BNB: {bnb_usd:.2f}\n📧 Stock: {stock}\n👥 Leads: {leads}\n🤖 Bots: {bots}")
                last_report = now
            time.sleep(60)
        except Exception as e:
            log(f"Erreur: {e}", "ERROR")
            time.sleep(60)

if __name__ == "__main__":
    main()
