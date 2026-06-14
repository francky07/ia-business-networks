#!/usr/bin/env python3
import time, os, json, sqlite3, subprocess, requests, smtplib, ssl
from email.mime.text import MIMEText
from datetime import datetime
from web3 import Web3
from neurone_module import NeuralNetwork   # Import du module indépendant

DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
LOG_FILE = os.path.expanduser("~/ceo_neurones.log")
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USER = "seckndananeuh@gmail.com"
SMTP_PASSWORD = "xsmtpsib-9364b75a7aa91f2040c5ccc04b90c01224b070f1efc4b97d5c21a896ec6e8527-BheO7lIdmm52XdF4"
PAYPAL_EMAIL = "faraseck@hotmail.fr"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

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
    sessions = [l for l in out.splitlines() if "ceo_neurones" not in l and l]
    return len(sessions)

def action_sell():
    log("ACTION: Vente massive")
    subprocess.run(["python", os.path.expanduser("~/departement_ventes/sell_emails_paypal.py")])

def action_marketing():
    log("ACTION marketing désactivée (SMTP invalide)", "WARNING")
    return
    # 
    log("ACTION: Campagne marketing par email")
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT email FROM leads WHERE contacte=0 LIMIT 50")
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
        log(f"Erreur marketing: {e}")
    finally:
        conn.close()

def action_recruit():
    log("ACTION: Recrutement d'un booster")
    subprocess.run(["tmux", "new-session", "-d", "-s", f"recruit_{int(time.time())}", "python ~/ia_booster_agence.py"], shell=True)

def action_invest():
    log("ACTION: Investissement (simulation)")

def main():
    log("CEO avec module neurones indépendant démarré")
    nn = NeuralNetwork(input_size=5, hidden_size=12, output_size=4)
    cycle, last_action, last_reward = 0, 0, 0.0
    while True:
        try:
            cycle += 1
            bnb = get_bnb_balance()
            rate = get_bnb_usd_rate()
            bnb_usd = bnb * rate
            stock, leads = get_db_stats()
            bots = get_bot_count()
            state = [min(1, stock/200), min(1, bnb_usd/5), min(1, leads/50), min(1, bots/30), (1 if bnb_usd < 1 and stock > 50 else 0)]
            now = time.time()
            if now - last_action >= 60:
                action = nn.predict_action(state)
                if action == 0: action_sell()
                elif action == 1: action_marketing()
                elif action == 2: action_recruit()
                elif action == 3: action_invest()
                reward = bnb_usd - last_reward
                nn.train(state, action, reward)
                last_reward, last_action = bnb_usd, now
                log(f"Cycle {cycle}: BNB={bnb_usd:.2f} USD, Stock={stock}, Leads={leads}, Bots={bots}, Action={action}, Reward={reward:.2f}")
            elif cycle % 10 == 0:
                log(f"Cycle {cycle}: BNB={bnb_usd:.2f} USD, Stock={stock}, Leads={leads}, Bots={bots}")
            time.sleep(60)
        except Exception as e:
            log(f"Erreur: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
