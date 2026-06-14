#!/usr/bin/env python3
import os, time, json, subprocess, threading, shutil, requests
from datetime import datetime
from web3 import Web3
from dotenv import load_dotenv

MEM_FILE = "ia_mem_pro.json"
WALLET_ADDR = "0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363"
BSC_RPC = "https://bsc-dataseed1.binance.org"
BACKUP_INTERVAL = 1800

def log(msg): print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def auto_backup():
    while True:
        time.sleep(BACKUP_INTERVAL)
        try:
            d = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(d, exist_ok=True)
            for f in ["ia_net_pro.py","ia_pi_agents.py","ia_booster_pro.py","ia_stability_agency.py","ia_mem_pro.json","index.html"]:
                if os.path.exists(f): shutil.copy2(f, d)
            for old in [x for x in os.listdir(".") if x.startswith("backup_") and os.path.isdir(x)]:
                if time.time() - os.path.getmtime(old) > 7*86400: shutil.rmtree(old)
            log("💾 Sauvegarde auto")
        except: pass
threading.Thread(target=auto_backup, daemon=True).start()

def repair_sessions():
    for sess,script in [("ia_net","ia_net_pro.py"),("pi_agents","ia_pi_agents.py"),("booster","ia_booster_pro.py"),("stability","ia_stability_agency.py")]:
        if subprocess.run(f"tmux has-session -t {sess}", shell=True).returncode != 0:
            log(f"🔄 Relance {sess}")
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

def get_status():
    s = {}
    try:
        with open("ia_net_pro.py") as f: c = f.read()
        import re
        tok = re.search(r'GITHUB_TOKEN = "(.*?)"', c).group(1)
        s["github"] = requests.get("https://api.github.com/user", headers={"Authorization": f"token {tok}"}, timeout=3).status_code == 200
    except: s["github"] = None
    try:
        bot = re.search(r'TELEGRAM_BOT_TOKEN = "(.*?)"', c).group(1)
        r = requests.get(f"https://api.telegram.org/bot{bot}/getMe", timeout=3)
        s["telegram"] = r.status_code == 200 and r.json().get("ok", False)
    except: s["telegram"] = None
    try:
        key = re.search(r'OPENAI_API_KEY = "(.*?)"', c).group(1)
        r = requests.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {key}"}, timeout=3)
        s["openai"] = r.status_code == 200
    except: s["openai"] = None
    try:
        load_dotenv(os.path.expanduser("~/ia_web/.env"))
        ik = os.getenv("INFURA_KEY")
        if ik:
            w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{ik}"))
            s["infura"] = w3.is_connected()
        pk = os.getenv("PI_API_KEY")
        if pk:
            r = requests.get("https://api.minepi.com/v2/me", headers={"Authorization": f"Key {pk}"}, timeout=3)
            s["pi"] = r.status_code == 200
    except: pass
    return s

def last_backup():
    dirs = [d for d in os.listdir(".") if d.startswith("backup_") and os.path.isdir(d)]
    if dirs:
        latest = max(dirs, key=os.path.getmtime)
        return f"{latest} ({datetime.fromtimestamp(os.path.getmtime(latest)).strftime('%H:%M')})"
    return "Aucune"

def logs(sess, n=6):
    try:
        out = subprocess.run(f"tmux capture-pane -pt {sess} -S -{n}", shell=True, capture_output=True, text=True)
        return out.stdout.splitlines()[-n:] or ["(aucun)"]
    except: return ["(session absente)"]

def proc_running(name):
    return subprocess.run(f"pgrep -f '{name}'", shell=True).returncode == 0

def main():
    log("Dashboard connectivité démarré")
    while True:
        repair_sessions()
        mem = get_mem()
        os.system('clear')
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║      IA NetSolutions PRO - Tableau de bord (connectivité)     ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"📊 CYCLE : {mem['stats'].get('cycle',0)} | ACTIONS : {mem['stats'].get('actions',0)} | ERR : {len(mem.get('errors',[]))}")
        print(f"💰 SOLDE BNB : {get_balance():.8f}\n")
        print("📌 DERNIER BOT LOG :")
        for l in logs("ia_net", 3): print(f"   {l}")
        print("\n📌 DERNIER BOOSTER LOG :")
        for l in logs("booster", 3): print(f"   {l}")
        st = get_status()
        print(f"\n🛡️ SERVICES : GitHub {('✅' if st.get('github') else '❌' if st.get('github') is False else '⚠️')} | Telegram {('✅' if st.get('telegram') else '❌' if st.get('telegram') is False else '⚠️')} | OpenAI {('✅' if st.get('openai') else '❌' if st.get('openai') is False else '⚠️')}")
        print(f"🔌 Infura {('✅' if st.get('infura') else '❌' if st.get('infura') is False else '⚠️')} | 🥧 Pi API {('✅' if st.get('pi') else '❌' if st.get('pi') is False else '⚠️')}")
        print(f"\n🖥️ PROCESSUS : Bot {'✅' if proc_running('ia_net_pro.py') else '❌'} | Pi {'✅' if proc_running('ia_pi_agents.py') else '❌'} | Booster {'✅' if proc_running('ia_booster_pro.py') else '❌'} | Stab {'✅' if proc_running('ia_stability_agency.py') else '❌'}")
        print(f"\n💾 DERNIÈRE SAUVEGARDE : {last_backup()}")
        print("\n🔄 Rafraîchi toutes les 5s (Ctrl+C pour quitter l'affichage)")
        time.sleep(5)

if __name__ == "__main__":
    main()
