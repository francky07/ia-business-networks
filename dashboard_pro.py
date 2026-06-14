#!/usr/bin/env python3
import os, time, json, subprocess, threading, shutil, requests
from datetime import datetime
from web3 import Web3

MEM_FILE = "ia_mem_pro.json"
BACKUP_INTERVAL = 1800  # 30 minutes
WALLET_ADDR = "0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363"
BSC_RPC = "https://bsc-dataseed1.binance.org"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[DASH {ts}] {msg}"
    print(line)

def auto_backup():
    while True:
        time.sleep(BACKUP_INTERVAL)
        try:
            backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)
            for f in ["ia_net_pro.py", "ia_pi_agents.py", "ia_booster_pro.py", "ia_stability_agency.py",
                      "ia_mem_pro.json", "index.html", "telegram_bot.py", "app.py"]:
                if os.path.exists(f):
                    shutil.copy2(f, backup_dir)
            for old in os.listdir("."):
                if old.startswith("backup_") and os.path.isdir(old):
                    if time.time() - os.path.getmtime(old) > 7*86400:
                        shutil.rmtree(old)
            log("💾 Sauvegarde auto effectuée")
        except Exception as e:
            log(f"❌ Sauvegarde: {e}")
threading.Thread(target=auto_backup, daemon=True).start()

def repair_sessions():
    for sess, script in [("ia_net","ia_net_pro.py"),("pi_agents","ia_pi_agents.py"),
                         ("booster","ia_booster_pro.py"),("stability","ia_stability_agency.py")]:
        if subprocess.run(f"tmux has-session -t {sess}", shell=True).returncode != 0:
            log(f"🔄 Redémarrage session {sess}")
            subprocess.run(f"tmux new-session -d -s {sess} 'python {script}'", shell=True)

def get_mem():
    try:
        with open(MEM_FILE) as f: return json.load(f)
    except: return {"stats":{"cycle":0,"actions":0},"errors":[]}

def get_balance():
    try:
        w3 = Web3(Web3.HTTPProvider(BSC_RPC))
        return w3.from_wei(w3.eth.get_balance(WALLET_ADDR), 'ether')
    except: return 0.0

def get_service_status():
    status = {}
    try:
        with open("ia_net_pro.py") as f: content = f.read()
        import re
        token = re.search(r'GITHUB_TOKEN = "(.*?)"', content).group(1)
        status["github"] = requests.get("https://api.github.com/user", headers={"Authorization": f"token {token}"}, timeout=3).status_code == 200
    except: status["github"] = None
    try:
        bot = re.search(r'TELEGRAM_BOT_TOKEN = "(.*?)"', content).group(1)
        r = requests.get(f"https://api.telegram.org/bot{bot}/getMe", timeout=3)
        status["telegram"] = r.status_code == 200 and r.json().get("ok", False)
    except: status["telegram"] = None
    try:
        key = re.search(r'OPENAI_API_KEY = "(.*?)"', content).group(1)
        r = requests.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {key}"}, timeout=3)
        status["openai"] = r.status_code == 200
    except: status["openai"] = None
    # Infura
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.expanduser("~/ia_web/.env"))
        infura_key = os.getenv("INFURA_KEY")
        if infura_key:
            w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{infura_key}"))
            status["infura"] = w3.is_connected()
        else:
            status["infura"] = None
    except: status["infura"] = False
    # Pi
    try:
        load_dotenv(os.path.expanduser("~/ia_web/.env"))
        pi_key = os.getenv("PI_API_KEY")
        if pi_key:
            r = requests.get("https://api.minepi.com/v2/me", headers={"Authorization": f"Key {pi_key}"}, timeout=3)
            status["pi"] = r.status_code == 200
        else:
            status["pi"] = None
    except: status["pi"] = False
    return status

def get_last_backup():
    backups = [d for d in os.listdir(".") if d.startswith("backup_") and os.path.isdir(d)]
    if backups:
        latest = max(backups, key=os.path.getmtime)
        return f"{latest} ({datetime.fromtimestamp(os.path.getmtime(latest)).strftime('%H:%M')})"
    return "Aucune"

def print_logs(sess, n=5):
    try:
        out = subprocess.run(f"tmux capture-pane -pt {sess} -S -{n}", shell=True, capture_output=True, text=True)
        lines = out.stdout.splitlines()
        return lines[-n:] if lines else ["(aucun log)"]
    except:
        return ["(session absente)"]

def main():
    log("Dashboard démarré")
    while True:
        repair_sessions()
        mem = get_mem()
        os.system('clear')
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║            IA NetSolutions PRO - Dashboard (live)                    ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"📊 CYCLE : {mem['stats'].get('cycle',0)}  |  ACTIONS : {mem['stats'].get('actions',0)}  |  ERREURS : {len(mem.get('errors',[]))}")
        print(f"💰 SOLDE BNB : {get_balance():.8f}\n")
        print("📌 BOT PRINCIPAL (dernières 5 lignes) :")
        for l in print_logs("ia_net",5): print(f"   {l}")
        print("\n📌 AGENTS Pi (dernières 5 lignes) :")
        for l in print_logs("pi_agents",5): print(f"   {l}")
        print("\n📌 BOOSTER (dernières 5 lignes) :")
        for l in print_logs("booster",5): print(f"   {l}")
        status = get_service_status()
        print(f"\n🛡️ SERVICES : GitHub {('✅' if status.get('github') else '❌' if status.get('github') is False else '⚠️')} | Telegram {('✅' if status.get('telegram') else '❌' if status.get('telegram') is False else '⚠️')} | OpenAI {('✅' if status.get('openai') else '❌' if status.get('openai') is False else '⚠️')}")
        print(f"🔌 Infura {('✅' if status.get('infura') else '❌' if status.get('infura') is False else '⚠️')} | 🥧 Pi API {('✅' if status.get('pi') else '❌' if status.get('pi') is False else '⚠️')}")
        print(f"\n🖥️ PROCESSUS : Bot principal {'✅' if subprocess.run('pgrep -f ia_net_pro.py', shell=True).returncode==0 else '❌'} | Agents Pi {'✅' if subprocess.run('pgrep -f ia_pi_agents.py', shell=True).returncode==0 else '❌'} | Booster {'✅' if subprocess.run('pgrep -f ia_booster_pro.py', shell=True).returncode==0 else '❌'} | Stabilité {'✅' if subprocess.run('pgrep -f ia_stability_agency.py', shell=True).returncode==0 else '❌'}")
        print(f"\n💾 DERNIÈRE SAUVEGARDE : {get_last_backup()}")
        print("\n🔄 Rafraîchi toutes les 5 secondes (Ctrl+C pour quitter l'affichage, le dashboard continue)")
        time.sleep(5)

if __name__ == "__main__":
    main()
