#!/usr/bin/env python3
"""
CEO GÉNIE EN INFORMATIQUE
Compétences réelles : optimisation système, nettoyage, surveillance, auto‑correction.
"""
import time, os, json, sqlite3, subprocess, requests, smtplib, ssl, glob, shutil
from datetime import datetime
from email.mime.text import MIMEText
from web3 import Web3

# ==================== CONFIGURATION ====================
DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
LOG_FILE = os.path.expanduser("~/ceo_genie_info.log")
STATE_FILE = os.path.expanduser("~/ceo_genie_info_state.json")
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USER = "seckndananeuh@gmail.com"
SMTP_PASSWORD = "xsmtpsib-9364b75a7aa91f2040c5ccc04b90c01224b070f1efc4b97d5c21a896ec6e8527-BheO7lIdmm52XdF4"
PAYPAL_EMAIL = "faraseck@hotmail.fr"

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

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
            log("Notification Telegram envoyée", "ACTION")
        except: pass

# ==================== COMPÉTENCES GÉNIE INFORMATIQUE ====================
def optimiser_base_sqlite():
    """Vide la base SQLite et réindexe pour libérer de l'espace"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("VACUUM")
        conn.execute("REINDEX")
        conn.close()
        log("Base SQLite optimisée (VACUUM + REINDEX)", "SYSTEM")
        return True
    except Exception as e:
        log(f"Erreur optimisation SQLite: {e}", "ERROR")
        return False

def nettoyer_logs_anciens(days=7):
    """Supprime les logs de plus de `days` jours"""
    log_files = glob.glob(os.path.expanduser("~/ia_ceo_state/*.log")) + \
                glob.glob(os.path.expanduser("~/cerebrum/logs/*.log")) + \
                glob.glob(os.path.expanduser("~/departement_ventes/*.log")) + \
                glob.glob(os.path.expanduser("~/ceo_*.log"))
    now = time.time()
    deleted = 0
    for f in log_files:
        if os.path.isfile(f) and now - os.path.getmtime(f) > days * 86400:
            os.remove(f)
            deleted += 1
    log(f"{deleted} anciens logs supprimés", "SYSTEM")
    return deleted

def surveiller_ressources():
    """Vérifie l'utilisation CPU, mémoire et espace disque, alerte si seuil dépassé"""
    try:
        # CPU (load average)
        load = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
        # Mémoire (via /proc/meminfo)
        with open("/proc/meminfo") as f:
            meminfo = f.read()
        mem_total = int([l for l in meminfo.splitlines() if "MemTotal" in l][0].split()[1])
        mem_avail = int([l for l in meminfo.splitlines() if "MemAvailable" in l][0].split()[1])
        mem_usage = (mem_total - mem_avail) / mem_total * 100
        # Espace disque (racine)
        disk = shutil.disk_usage("/")
        disk_usage = (disk.used / disk.total) * 100
        if load > 2.0 or mem_usage > 80 or disk_usage > 85:
            alert = f"⚠️ Ressources élevées : CPU load={load:.2f}, Mémoire={mem_usage:.1f}%, Disque={disk_usage:.1f}%"
            log(alert, "WARNING")
            send_telegram(alert)
        return {"load": load, "mem_usage": mem_usage, "disk_usage": disk_usage}
    except Exception as e:
        log(f"Erreur surveillance ressources: {e}", "ERROR")
        return {}

def redemarrer_bot_dead(bot_name):
    """Redémarre un bot tmux s'il n'est pas actif"""
    out = subprocess.run(["tmux", "ls"], capture_output=True, text=True).stdout
    if bot_name not in out:
        log(f"Bot {bot_name} absent → redémarrage", "SYSTEM")
        if bot_name == "agence_kays":
            subprocess.run(["tmux", "new-session", "-d", "-s", "agence_kays", "python ~/agence_kays/agence.py"], shell=True)
        elif bot_name == "ventes":
            subprocess.run(["tmux", "new-session", "-d", "-s", "ventes", "cd ~/departement_ventes && python ventes.py"], shell=True)
        elif bot_name == "ia_net":
            subprocess.run(["tmux", "new-session", "-d", "-s", "ia_net", "python ~/ia_net_pro.py"], shell=True)
        # Ajoutez d'autres bots ici
        send_telegram(f"🔄 Bot {bot_name} redémarré automatiquement.")

def nettoyer_memoire_cache():
    """Libère le cache système (nécessite root, mais on peut le tenter)"""
    try:
        with open("/proc/sys/vm/drop_caches", "w") as f:
            f.write("3")
        log("Cache mémoire vidé (drop_caches=3)", "SYSTEM")
    except:
        log("Impossible de vider le cache (pas root)", "WARNING")

def analyser_performances():
    """Simule une analyse des performances (logs, erreurs) et propose des optimisations"""
    # Compter les erreurs récentes dans les logs
    err_count = 0
    for log_file in glob.glob("~/ia_ceo_state/*.log"):
        try:
            with open(log_file) as f:
                err_count += sum(1 for line in f if "ERROR" in line or "Exception" in line)
        except: pass
    if err_count > 50:
        log(f"Nombre élevé d'erreurs récentes : {err_count}", "WARNING")
        send_telegram(f"⚠️ {err_count} erreurs détectées dans les logs – vérifier les bots.")
    return err_count

# ==================== ACTIONS BUSINESS (déjà existantes) ====================
def action_vendre():
    log("ACTION: Vente massive", "ACTION")
    subprocess.run(["python", os.path.expanduser("~/departement_ventes/sell_emails_paypal.py")])

def action_marketing():
    log("ACTION: Campagne marketing par email", "ACTION")
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT email FROM leads WHERE contacte=0 LIMIT 50")
        leads = c.fetchall()
        if not leads:
            return
        subject = "Offre spéciale IA Business"
        body = f"""<html><body><h2>Bonjour,</h2><p>Liste d'emails vérifiés à 0.01 USD/email. <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&amount=1.00&currency_code=USD">Acheter</a></p></body></html>"""
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            for (email,) in leads:
                msg = MIMEText(body, 'html')
                msg['Subject'] = subject
                msg['From'] = SMTP_USER
                msg['To'] = email
                server.send_message(msg)
            c.execute("UPDATE leads SET contacte=1 WHERE contacte=0")
            conn.commit()
        log(f"Email envoyé à {len(leads)} leads", "ACTION")
        send_telegram(f"📢 Campagne marketing : {len(leads)} leads contactés.")
    except Exception as e:
        log(f"Erreur marketing: {e}", "ERROR")
    finally:
        conn.close()

def action_recruter():
    log("ACTION: Recrutement d'un booster", "ACTION")
    subprocess.run(["tmux", "new-session", "-d", "-s", f"recruit_{int(time.time())}", "python ~/ia_booster_agence.py"], shell=True)

def action_augmenter_prix():
    state = load_state()
    new_price = round(state.get("prix_email", 0.01) + 0.005, 3)
    state["prix_email"] = new_price
    save_state(state)
    subprocess.run(f"sed -i 's/montant = nb \\* [0-9.]*/montant = nb * {new_price}/' ~/departement_ventes/sell_emails_paypal.py", shell=True)
    log(f"Prix augmenté à {new_price} USD", "ACTION")

def action_diminuer_prix():
    state = load_state()
    new_price = max(0.002, state.get("prix_email", 0.01) - 0.005)
    state["prix_email"] = round(new_price, 3)
    save_state(state)
    subprocess.run(f"sed -i 's/montant = nb \\* [0-9.]*/montant = nb * {new_price}/' ~/departement_ventes/sell_emails_paypal.py", shell=True)
    log(f"Prix diminué à {new_price} USD", "ACTION")

def action_investir():
    log("ACTION: Investissement (lance deux boosters)", "ACTION")
    for _ in range(2):
        subprocess.run(["tmux", "new-session", "-d", "-s", f"invest_{int(time.time())}", "python ~/ia_booster_agence.py"], shell=True)
    send_telegram("🚀 Investissement réalisé : deux boosters supplémentaires.")

# ==================== COLLECTE DE DONNÉES ====================
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
    sessions = [l for l in out.splitlines() if "ceo_genie_info" not in l and l]
    return len(sessions)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"seuil_vente": 10, "prix_email": 0.01, "objectif_revenu": 10.0, "derniere_action": ""}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# ==================== BOUCLE PRINCIPALE (avec compétences info) ====================
def main():
    log("🧠 CEO GÉNIE INFORMATIQUE – Compétences système réelles", "START")
    state = load_state()
    cycle = 0
    last_optim = 0
    last_clean = 0
    last_health = 0

    while True:
        try:
            cycle += 1
            bnb = get_bnb_balance()
            rate = get_bnb_usd_rate()
            bnb_usd = bnb * rate
            stock, leads = get_db_stats()
            bots = get_bot_count()
            log(f"Cycle {cycle}: BNB={bnb_usd:.2f} | Stock={stock} | Leads={leads} | Bots={bots}")

            # Décisions business (comme avant)
            if stock > state["seuil_vente"]:
                action_vendre()
            elif leads > 10 and stock > 20:
                action_marketing()
            elif bots < 10:
                action_recruter()
            if stock > 500:
                action_diminuer_prix()
            elif stock < 50 and bnb_usd > 1:
                action_augmenter_prix()
            if bnb_usd > 5 and stock > 200:
                action_investir()

            # ========== COMPÉTENCES INFORMATIQUES (tâches périodiques) ==========
            now = time.time()
            # Optimiser la base SQLite toutes les 6 heures
            if now - last_optim > 21600:
                optimiser_base_sqlite()
                last_optim = now
            # Nettoyer les logs tous les jours
            if now - last_clean > 86400:
                nettoyer_logs_anciens()
                last_clean = now
            # Surveiller les ressources toutes les 5 minutes
            if now - last_health > 300:
                surveiller_ressources()
                analyser_performances()
                # Redémarrer les bots manquants (ex: agence_kays, ventes)
                for bot in ["agence_kays", "ventes", "ia_net"]:
                    redemarrer_bot_dead(bot)
                last_health = now

            # Ajustement adaptatif du seuil de vente
            if bnb_usd > 1 and stock > 10:
                state["seuil_vente"] = max(5, state["seuil_vente"] - 1)
            elif bnb_usd < 0.1 and stock > 100:
                state["seuil_vente"] = min(20, state["seuil_vente"] + 1)
            save_state(state)

            # Rapport horaire (simplifié)
            if cycle % 60 == 0:
                rapport = f"📊 RAPPORT GÉNIE INFO - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n💰 BNB: {bnb_usd:.2f} USD\n📧 Stock: {stock}\n👥 Leads: {leads}\n🤖 Bots: {bots}\n⚙️ Seuil: {state['seuil_vente']} | Prix: {state['prix_email']} USD"
                log(rapport, "REPORT")
                send_telegram(rapport)

            time.sleep(60)
        except Exception as e:
            log(f"Erreur critique: {e}", "ERROR")
            time.sleep(60)

if __name__ == "__main__":
    main()
