#!/usr/bin/env python3
"""
IA NetSolutions - Agence de stabilité (250 agents)
Surveillance : processus, tmux, API, mémoire, logs.
Auto-réparation : redémarrage, correction des erreurs connues (PiFraud, etc.).
"""
import os, time, json, subprocess, requests, threading, re
from datetime import datetime
from web3 import Web3

# ---------- Configuration ----------
BSC_RPC = "https://bsc-dataseed1.binance.org"
WALLET_ADDR = "0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363"
MEM_FILE = "ia_mem_pro.json"
LOG_FILE = "stability.log"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[STABILITY {ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# ---------- Utilitaires ----------
def is_process_running(script_name):
    try:
        result = subprocess.run(f"pgrep -f '{script_name}'", shell=True, capture_output=True)
        return result.returncode == 0
    except: return False

def restart_tmux_session(session_name, script_path):
    subprocess.run(f"tmux kill-session -t {session_name} 2>/dev/null", shell=True)
    time.sleep(1)
    subprocess.run(f"tmux new-session -d -s {session_name} 'python {script_path}'", shell=True)
    log(f"🔄 Session {session_name} redémarrée (script {script_path})")

def check_tmux_session(session_name):
    result = subprocess.run(f"tmux has-session -t {session_name} 2>/dev/null", shell=True)
    return result.returncode == 0

def get_memory_stats():
    if os.path.exists(MEM_FILE):
        try:
            with open(MEM_FILE, "r") as f:
                return json.load(f)
        except: pass
    return {}

def fix_pifraud_error():
    """Corrige la classe PiFraud dans ia_pi_agents.py si l'erreur est détectée"""
    if not os.path.exists("ia_pi_agents.py"):
        return
    with open("ia_pi_agents.py", "r") as f:
        content = f.read()
    # Vérifier si l'ancienne version problématique existe
    if "class PiFraud(PiBaseAgent):" in content and "def execute(self):" in content:
        # Version corrigée
        new_class = '''class PiFraud(PiBaseAgent):
    def execute(self):
        mem = load_memory()
        payments = mem.get("pi_payments", [])
        for p in payments:
            if isinstance(p, dict):
                try:
                    amount = float(p.get("amount", 0))
                    if amount > 1000:
                        print(f"[PiFraud] Suspect: {p}")
                except:
                    pass'''
        # Remplacer l'ancienne implémentation
        import re
        pattern = r'class PiFraud\(PiBaseAgent\):.*?def execute\(self\):.*?(?=\n\n|\Z)'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, new_class, content, flags=re.DOTALL)
            with open("ia_pi_agents.py", "w") as f:
                f.write(content)
            log("🔧 Correction PiFraud appliquée (ia_pi_agents.py)")
            return True
    return False

def fix_pi_api_key():
    """Vérifie et alerte si la clé Pi API est manquante/invalide"""
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.expanduser("~/ia_web/.env"))
        pi_key = os.getenv("PI_API_KEY")
        if not pi_key:
            log("⚠️ Pi API key manquante dans .env – veuillez l'ajouter")
            return False
        r = requests.get("https://api.minepi.com/v2/me", headers={"Authorization": f"Key {pi_key}"}, timeout=5)
        if r.status_code != 200:
            log("❌ Pi API clé invalide – vérifiez votre clé")
            return False
        return True
    except Exception as e:
        log(f"⚠️ Erreur vérification Pi API: {e}")
        return False

# ---------- Agents ----------
class StabilityAgent(threading.Thread):
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
                    log(f"❌ Erreur dans {self.name}: {e}")
            time.sleep(5)
    def execute(self):
        pass

# 1. ProcessWatchdog (80)
class ProcessWatchdog(StabilityAgent):
    def execute(self):
        if not is_process_running("ia_net_pro.py"):
            log("⚠️ Bot principal arrêté → redémarrage")
            restart_tmux_session("ia_net", "ia_net_pro.py")
        if not is_process_running("ia_pi_agents.py"):
            log("⚠️ Agents Pi arrêtés → redémarrage")
            restart_tmux_session("pi_agents", "ia_pi_agents.py")
        if not is_process_running("ia_booster_pro.py"):
            log("⚠️ Booster arrêté → redémarrage")
            restart_tmux_session("booster", "ia_booster_pro.py")
        if not is_process_running("pi_backend.py"):
            log("⚠️ Backend Pi arrêté → redémarrage")
            subprocess.run("cd ~/ia_web && nohup python pi_backend.py > pi_backend.log 2>&1 &", shell=True)
            log("✅ Backend Pi relancé")

for i in range(80):
    ProcessWatchdog(f"ProcWatch_{i}", interval=60).start()

# 2. TmuxWatchdog (40)
class TmuxWatchdog(StabilityAgent):
    def execute(self):
        for sess in ["ia_net", "pi_agents", "booster"]:
            if not check_tmux_session(sess):
                log(f"⚠️ Session tmux {sess} manquante → recréation")
                script = {"ia_net": "ia_net_pro.py", "pi_agents": "ia_pi_agents.py", "booster": "ia_booster_pro.py"}[sess]
                subprocess.run(f"tmux new-session -d -s {sess} 'python {script}'", shell=True)
                log(f"✅ Session {sess} recréée")

for i in range(40):
    TmuxWatchdog(f"TmuxWatch_{i}", interval=90).start()

# 3. APIMonitor (50)
class APIMonitor(StabilityAgent):
    def execute(self):
        # BSC
        try:
            w3 = Web3(Web3.HTTPProvider(BSC_RPC))
            if w3.is_connected():
                bal = w3.from_wei(w3.eth.get_balance(WALLET_ADDR), 'ether')
                log(f"💰 BSC OK - Solde: {bal:.8f}")
            else:
                log("❌ BSC déconnecté")
        except Exception as e:
            log(f"❌ BSC error: {e}")
        # GitHub
        token = None
        try:
            with open("ia_net_pro.py") as f:
                for line in f:
                    if line.startswith("GITHUB_TOKEN"):
                        token = line.split('"')[1]
                        break
            if token:
                r = requests.get("https://api.github.com/user", headers={"Authorization": f"token {token}"}, timeout=5)
                if r.status_code == 200:
                    log("✅ GitHub OK")
                else:
                    log("❌ GitHub token invalide")
        except Exception as e:
            log(f"❌ GitHub erreur: {e}")
        # Telegram
        try:
            bot = None
            with open("ia_net_pro.py") as f:
                for line in f:
                    if line.startswith("TELEGRAM_BOT_TOKEN"):
                        bot = line.split('"')[1]
                        break
            if bot:
                r = requests.get(f"https://api.telegram.org/bot{bot}/getMe", timeout=5)
                if r.status_code == 200 and r.json()["ok"]:
                    log("✅ Telegram OK")
                else:
                    log("❌ Telegram bot injoignable")
        except: pass
        # OpenAI
        try:
            key = None
            with open("ia_net_pro.py") as f:
                for line in f:
                    if line.startswith("OPENAI_API_KEY"):
                        key = line.split('"')[1]
                        break
            if key:
                r = requests.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {key}"}, timeout=5)
                if r.status_code == 200:
                    log("✅ OpenAI OK")
                else:
                    log("❌ OpenAI clé invalide/quota")
        except: pass
        # Infura
        try:
            from dotenv import load_dotenv
            load_dotenv(os.path.expanduser("~/ia_web/.env"))
            infura_key = os.getenv("INFURA_KEY")
            if infura_key:
                w3_inf = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{infura_key}"))
                if w3_inf.is_connected():
                    log("✅ Infura OK")
                else:
                    log("❌ Infura déconnecté")
        except: pass
        # Pi API avec auto-alerte
        try:
            from dotenv import load_dotenv
            load_dotenv(os.path.expanduser("~/ia_web/.env"))
            pi_key = os.getenv("PI_API_KEY")
            if not pi_key:
                log("⚠️ Pi API key manquante – veuillez la configurer dans ~/ia_web/.env")
            else:
                r = requests.get("https://api.minepi.com/v2/me", headers={"Authorization": f"Key {pi_key}"}, timeout=5)
                if r.status_code == 200:
                    log("✅ Pi API OK")
                else:
                    log("❌ Pi API erreur (clé invalide ou réseau)")
        except Exception as e:
            log(f"❌ Pi API exception: {e}")

for i in range(50):
    APIMonitor(f"APIMon_{i}", interval=120).start()

# 4. MemoryWatchdog (30) – avec auto-réparation
class MemoryWatchdog(StabilityAgent):
    def execute(self):
        mem = get_memory_stats()
        errors = mem.get("errors", [])
        if len(errors) > 50:
            log(f"⚠️ Trop d'erreurs ({len(errors)}) → nettoyage mémoire")
            mem["errors"] = errors[-20:]
            with open(MEM_FILE, "w") as f:
                json.dump(mem, f, indent=2)
            log("✅ Mémoire nettoyée (20 dernières erreurs conservées)")
        if not os.path.exists(MEM_FILE):
            log("⚠️ Fichier mémoire absent → recréation")
            default = {"stats":{"cycle":0,"actions":0},"errors":[],"last_balance":0.0}
            with open(MEM_FILE, "w") as f:
                json.dump(default, f, indent=2)
            log("✅ Fichier mémoire recréé")

for i in range(30):
    MemoryWatchdog(f"MemWatch_{i}", interval=300).start()

# 5. LogWatchdog (50) – avec auto-correction des erreurs détectées
class LogWatchdog(StabilityAgent):
    def execute(self):
        # Analyser les logs tmux pour détecter des erreurs récurrentes
        for sess in ["ia_net", "pi_agents", "booster"]:
            try:
                output = subprocess.run(f"tmux capture-pane -pt {sess} -S -50", shell=True, capture_output=True, text=True)
                lines = output.stdout.splitlines()
                # Détection de l'erreur PiFraud
                if any("PiFraud" in l and "object has no attribute 'get'" in l for l in lines):
                    log("⚠️ Erreur PiFraud détectée dans pi_agents → tentative de correction")
                    if fix_pifraud_error():
                        log("🔄 Redémarrage des agents Pi après correction")
                        restart_tmux_session("pi_agents", "ia_pi_agents.py")
                # Détection d'autres erreurs critiques (à étendre)
                if any("No module named" in l for l in lines):
                    log("⚠️ Erreur d'import détectée – redémarrage du service concerné")
                    if sess == "pi_agents":
                        restart_tmux_session("pi_agents", "ia_pi_agents.py")
                    elif sess == "ia_net":
                        restart_tmux_session("ia_net", "ia_net_pro.py")
                    elif sess == "booster":
                        restart_tmux_session("booster", "ia_booster_pro.py")
            except Exception as e:
                log(f"❌ Erreur analyse logs {sess}: {e}")

for i in range(50):
    LogWatchdog(f"LogWatch_{i}", interval=180).start()

log("🚀 Agence de stabilité démarrée (250 agents actifs) – auto-correction active")
while True:
    time.sleep(30)
