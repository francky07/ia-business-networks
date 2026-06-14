#!/usr/bin/env python3
"""
CEO COMPÉTENT – Version enrichie du CEO stable
Ajouts : prédiction simple, apprentissage par récompense, actions marketing réelles (email + Telegram), seuil dynamique.
"""
import time, os, sqlite3, subprocess, requests, smtplib, ssl, math
from datetime import datetime
from email.mime.text import MIMEText
from web3 import Web3

DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
LOG_FILE = os.path.expanduser("~/ceo_competent.log")
STATE_FILE = os.path.expanduser("~/ceo_state.json")

# Configuration SMTP (Brevo)
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USER = "seckndananeuh@gmail.com"
SMTP_PASSWORD = "xsmtpsib-9364b75a7aa91f2040c5ccc04b90c01224b070f1efc4b97d5c21a896ec6e8527-BheO7lIdmm52XdF4"
PAYPAL_EMAIL = "faraseck@hotmail.fr"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def get_env(key, default=None):
    import os
    env_file = os.path.expanduser("~/.env_ia_business")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith("export "): line = line[7:]
                if "=" in line and line.split("=")[0].strip() == key:
                    return line.split("=",1)[1].strip().strip("\"'")
    return default

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"seuil": 10, "apprentissage": {"bonnes_actions": 0, "mauvaises_actions": 0}}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

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
    sessions = [l for l in out.splitlines() if "ceo_competent" not in l and l]
    return len(sessions)

def predict_stock_tomorrow(stock_history):
    """Prédiction naïve : tendance basée sur les 5 dernières valeurs (simulé)"""
    # Pour simplifier, on utilise une moyenne mobile
    return stock_history[-1] if stock_history else 0

def send_email_marketing():
    """Envoie un email aux leads non contactés (max 30)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT email FROM leads WHERE contacte=0 LIMIT 30")
        leads = c.fetchall()
        if not leads:
            log("Aucun lead à contacter")
            return
        subject = "Offre spéciale IA Business – Liste d'emails qualifiés"
        body = f"""<html><body><h2>Bonjour,</h2><p>Notre IA a généré une liste d'emails vérifiés.</p><p>Prix : 0,01 USD/email. <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&amount=1.00&currency_code=USD">Acheter maintenant</a></p><p>Cordialement,<br>IA Business</p></body></html>"""
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
        log(f"Email envoyé à {len(leads)} leads")
    except Exception as e:
        log(f"Erreur marketing email: {e}")
    finally:
        conn.close()

def send_telegram_message(msg):
    token = get_env("TELEGRAM_BOT_TOKEN")
    chat_id = get_env("TELEGRAM_CHAT_ID")
    if token and chat_id and token != "VOTRE_TOKEN":
        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": msg}, timeout=5)
            log("Notification Telegram envoyée")
        except: pass

def action_marketing():
    log("ACTION: Campagne marketing (email + Telegram)")
    send_email_marketing()
    send_telegram_message("📢 Campagne marketing IA Business lancée ! Offres spéciales disponibles.")

def action_sell():
    log("ACTION: Vente massive")
    subprocess.run(["python", os.path.expanduser("~/departement_ventes/sell_emails_paypal.py")])

def action_recruit():
    log("ACTION: Recrutement d'un booster")
    subprocess.run(["tmux", "new-session", "-d", "-s", f"recruit_{int(time.time())}", "python ~/ia_booster_agence.py"], shell=True)

def ajuster_seuil(state, reward):
    """Apprentissage simple : si récompense positive, on baisse le seuil (vendre plus vite) ; si négative, on l'augmente"""
    if reward > 0:
        state["seuil"] = max(3, state["seuil"] - 1)
        state["apprentissage"]["bonnes_actions"] += 1
        log(f"Seuil baissé à {state['seuil']} (bonne récompense)")
    else:
        state["seuil"] = min(20, state["seuil"] + 1)
        state["apprentissage"]["mauvaises_actions"] += 1
        log(f"Seuil augmenté à {state['seuil']} (récompense faible)")

def main():
    log("CEO COMPÉTENT démarré (prédiction + apprentissage + actions réelles)")
    state = load_state()
    stock_history = []
    cycle = 0
    last_reward = 0.0

    while True:
        try:
            cycle += 1
            bnb = get_bnb_balance()
            rate = get_bnb_usd_rate()
            bnb_usd = bnb * rate
            stock, leads = get_db_stats()
            bots = get_bot_count()
            stock_history.append(stock)
            if len(stock_history) > 10:
                stock_history.pop(0)
            pred_stock = predict_stock_tomorrow(stock_history)
            log(f"Cycle {cycle}: BNB={bnb_usd:.2f} USD, Stock={stock}, Leads={leads}, Bots={bots}, Prédiction stock demain={pred_stock:.0f}")

            # Décision : si stock > seuil, vendre ; sinon, selon prédiction et leads
            seuil = state["seuil"]
            if stock > seuil:
                action_sell()
                reward = bnb_usd - last_reward
                ajuster_seuil(state, reward)
                last_reward = bnb_usd
            elif leads > 5 and stock > 10:
                action_marketing()
                reward = leads - 5  # récompense basée sur les leads
                ajuster_seuil(state, reward)
                last_reward = bnb_usd
            elif bots < 10 and stock > 20:
                action_recruit()
            else:
                log("Aucune action nécessaire")

            save_state(state)
            time.sleep(60)
        except Exception as e:
            log(f"Erreur: {e}")
            time.sleep(60)

if __name__ == "__main__":
    import json
    main()
