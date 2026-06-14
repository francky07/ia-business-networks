#!/usr/bin/env python3
import os, time, json, subprocess, threading, shutil, requests
from datetime import datetime
from web3 import Web3
from dotenv import load_dotenv

# ---------- Configuration ----------
MEM_FILE = "ia_mem_pro.json"
BACKUP_INTERVAL = 1800  # 30 secondes pour test, 1800 pour production
WALLET_ADDR = "0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363"
BSC_RPC = "https://bsc-dataseed1.binance.org"
LOG_FILE = "dashboard.log"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[DASH {ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# ---------- Auto‑sauvegarde ----------
def auto_backup():
    while True:
        time.sleep(BACKUP_INTERVAL)
        try:
            backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)
            for f in ["ia_net_pro.py", "ia_pi_agents.py", "ia_booster_pro.py",
                      "ia_stability_agency.py", "ia_mem_pro.json", "index.html",
                      "telegram_bot.py", "app.py"]:
                if os.path.exists(f):
                    shutil.copy2(f, backup_dir)
            # Supprimer les sauvegardes de plus de 7 jours
            for d in os.listdir("."):
                if d.startswith("backup_") and os.path.isdir(d):
                    if time.time() - os.path.getmtime(d) > 7*86400:
                        shutil.rmtree(d)
            log("💾 Sauvegarde automatique effectuée")
        except Exception as e:
            log(f"❌ Erreur sauvegarde: {e}")
threading.Thread(target=auto_backup, daemon=True).start()

# ---------- Auto‑dépannage sessions tmux ----------
def repair_sessions():
    for sess, script in [("ia_net","ia_net_pro.py"), ("pi_agents","ia_pi_agents.py"),
                         ("booster","ia_booster_pro.py"), ("stability","ia_stability_agency.py")]:
        if subprocess.run(f"tmux has-session -t {sess}", shell=True).returncode != 0:
            log(f"🔄 Redémarrage de {sess}")
            subprocess.run(f"tmux new-session -d -s {sess} 'python {script}'", shell=True)

# ---------- Récupération des données ----------
def get_memory():
    try:
        with open(MEM_FILE) as f:
            return json.load(f)
    except:
        return {"stats":{"cycle":0,"actions":0},"errors":[]}

def get_balance():
    try:
        w3 = Web3(Web3.HTTPProvider(BSC_RPC))
        return w3.from_wei(w3.eth.get_balance(WALLET_ADDR), 'ether')
    except:
        return 0.0

def get_service_status():
    status = {"github": None, "telegram": None, "openai": None, "infura": None, "pi": None}
    try:
        with open("ia_net_pro.py") as f:
            content = f.read()
        import re
        # GitHub
        token = re.search(r'GITHUB_TOKEN = "(.*?)"', content).group(1)
        if token:
            r = requests.get("https://api.github.com/user", headers={"Authorization": f"token {token}"}, timeout=3)
            status["github"] = r.status_code == 200
        # Telegram
        bot = re.search(r'TELEGRAM_BOT_TOKEN = "(.*?)"', content).group(1)
        if bot:
            r = requests.get(f"https://api.telegram.org/bot{bot}/getMe", timeout=3)
            status["telegram"] = r.status_code == 200 and r.json().get("ok", False)
        # OpenAI
        key = re.search(r'OPENAI_API_KEY = "(.*?)"', content).group(1)
        if key:
            r = requests.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {key}"}, timeout=3)
            status["openai"] = r.status_code == 200
    except: pass
    # Infura et Pi via .env
    try:
        load_dotenv(os.path.expanduser("~/ia_web/.env"))
        infura_key = os.getenv("INFURA_KEY")
        if infura_key:
            w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{infura_key}"))
            status["infura"] = w3.is_connected()
        pi_key = os.getenv("PI_API_KEY")
        if pi_key:
            r = requests.get("https://api.minepi.com/v2/me", headers={"Authorization": f"Key {pi_key}"}, timeout=3)
            status["pi"] = r.status_code == 200
    except: pass
    return status

def get_last_backup():
    backups = [d for d in os.listdir(".") if d.startswith("backup_") and os.path.isdir(d)]
    if backups:
        latest = max(backups, key=os.path.getmtime)
        return f"{latest} ({datetime.fromtimestamp(os.path.getmtime(latest)).strftime('%H:%M')})"
    return "Aucune"

def get_tmux_logs(sess, n=6):
    try:
        out = subprocess.run(f"tmux capture-pane -pt {sess} -S -{n}", shell=True, capture_output=True, text=True)
        lines = out.stdout.splitlines()
        return lines[-n:] if lines else ["(aucun log)"]
    except:
        return ["(session absente)"]

def process_running(name):
    return subprocess.run(f"pgrep -f '{name}'", shell=True).returncode == 0

# ---------- Boucle principale ----------
def main():
    log("Dashboard all-in-one démarré")
    while True:
        repair_sessions()
        mem = get_memory()
        os.system('clear')
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║         IA NetSolutions PRO - Dashboard All-in-One                  ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"📊 CYCLE : {mem['stats'].get('cycle',0)}  |  ACTIONS : {mem['stats'].get('actions',0)}  |  ERREURS : {len(mem.get('errors',[]))}")
        print(f"💰 SOLDE BNB : {get_balance():.8f}\n")
        print("📌 BOT PRINCIPAL (logs récents) :")
        for l in get_tmux_logs("ia_net", 5): print(f"   {l}")
        print("\n📌 AGENTS Pi :")
        for l in get_tmux_logs("pi_agents", 5): print(f"   {l}")
        print("\n📌 BOOSTER :")
        for l in get_tmux_logs("booster", 5): print(f"   {l}")
        status = get_service_status()
        print(f"\n🛡️ SERVICES : GitHub {('✅' if status['github'] else '❌' if status['github'] is False else '⚠️')} | Telegram {('✅' if status['telegram'] else '❌' if status['telegram'] is False else '⚠️')} | OpenAI {('✅' if status['openai'] else '❌' if status['openai'] is False else '⚠️')}")
        print(f"🔌 Infura {('✅' if status['infura'] else '❌' if status['infura'] is False else '⚠️')} | 🥧 Pi API {('✅' if status['pi'] else '❌' if status['pi'] is False else '⚠️')}")
        print(f"\n🖥️ PROCESSUS : Bot principal {'✅' if process_running('ia_net_pro.py') else '❌'} | Agents Pi {'✅' if process_running('ia_pi_agents.py') else '❌'} | Booster {'✅' if process_running('ia_booster_pro.py') else '❌'} | Stabilité {'✅' if process_running('ia_stability_agency.py') else '❌'}")
        print(f"\n💾 DERNIÈRE SAUVEGARDE : {get_last_backup()}")
        print("\n🔄 Rafraîchi toutes les 5 secondes (Ctrl+C pour quitter l'affichage, le dashboard continue)")
        time.sleep(5)

if __name__ == "__main__":
    main()
