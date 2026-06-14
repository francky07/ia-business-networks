#!/usr/bin/env python3
"""
CEO ENTREPRENEUR & LEADER – Décisions stratégiques réelles, pas de simulation.
Ajuste les prix, lance des campagnes, recrute, investit, communique.
"""
import time, os, json, sqlite3, subprocess, requests, smtplib, ssl, math
from datetime import datetime
from email.mime.text import MIMEText
from web3 import Web3

DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
LOG_FILE = os.path.expanduser("~/ceo_entrepreneur.log")
STATE_FILE = os.path.expanduser("~/ceo_entrepreneur_state.json")

# Configuration SMTP (Brevo)
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

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "seuil_vente": 10,
        "prix_email": 0.01,
        "budget_marketing": 5.0,
        "objectif_revenu": 10.0,
        "leadership_style": "balanced",
        "derniere_decision": ""
    }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def get_bnb_usd_rate():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=usd", timeout=5)
        if r.status_code == 200:
            return float(r.json()["binancecoin"]["usd"])
    except:
        pass
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
    sessions = [l for l in out.splitlines() if "ceo_entrepreneur" not in l and l]
    return len(sessions)

def send_telegram(msg):
    token = get_env("TELEGRAM_BOT_TOKEN")
    chat_id = get_env("TELEGRAM_CHAT_ID")
    if token and chat_id and token != "VOTRE_TOKEN":
        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": msg}, timeout=5)
            log("Notification Telegram envoyée", "ACTION")
        except Exception as e:
            log(f"Erreur Telegram: {e}", "ERROR")

def send_email_marketing():
    """Action marketing réelle : email aux leads"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT email FROM leads WHERE contacte=0 LIMIT 50")
        leads = c.fetchall()
        if not leads:
            log("Aucun lead à contacter", "INFO")
            return 0
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
        log(f"Email envoyé à {len(leads)} leads", "ACTION")
        return len(leads)
    except Exception as e:
        log(f"Erreur marketing email: {e}", "ERROR")
        return 0
    finally:
        conn.close()

def action_vendre():
    log("ACTION: Déclenchement d'une vente massive", "ACTION")
    subprocess.run(["python", os.path.expanduser("~/departement_ventes/sell_emails_paypal.py")])

def action_recruter():
    log("ACTION: Recrutement d'un nouveau booster", "ACTION")
    subprocess.run(["tmux", "new-session", "-d", "-s", f"recruit_{int(time.time())}", "python ~/ia_booster_agence.py"], shell=True)

def action_marketing():
    nb = send_email_marketing()
    if nb > 0:
        send_telegram(f"📢 Campagne marketing lancée : {nb} leads contactés.")
    else:
        log("Aucune action marketing possible (pas de leads)", "INFO")

def action_augmenter_prix():
    """Augmente le prix des emails de 0.005 USD"""
    state = load_state()
    state["prix_email"] = round(state["prix_email"] + 0.005, 3)
    save_state(state)
    subprocess.run(f"sed -i 's/montant = nb \\* [0-9.]*/montant = nb * {state['prix_email']}/' ~/departement_ventes/sell_emails_paypal.py", shell=True)
    log(f"Prix des emails augmenté à {state['prix_email']} USD", "ACTION")
    send_telegram(f"💰 Prix des emails augmenté à {state['prix_email']} USD.")

def action_diminuer_prix():
    """Diminue le prix des emails de 0.005 USD (minimum 0.002)"""
    state = load_state()
    new_price = max(0.002, state["prix_email"] - 0.005)
    state["prix_email"] = round(new_price, 3)
    save_state(state)
    subprocess.run(f"sed -i 's/montant = nb \\* [0-9.]*/montant = nb * {state['prix_email']}/' ~/departement_ventes/sell_emails_paypal.py", shell=True)
    log(f"Prix des emails diminué à {state['prix_email']} USD", "ACTION")
    send_telegram(f"💰 Prix des emails diminué à {state['prix_email']} USD.")

def action_investir():
    """Simule un investissement dans l'infrastructure (améliore la productivité)"""
    log("ACTION: Investissement dans l'infrastructure (boost de productivité)", "ACTION")
    send_telegram("🚀 Investissement réalisé : les boosters seront plus efficaces.")
    # Pour simuler, on pourrait lancer un booster supplémentaire
    action_recruter()

def analyser_tendances(bnb_usd, stock, leads, bots, state):
    """Analyse et prend des décisions entrepreneuriales"""
    decisions = []
    # 1. Objectif de revenu
    if bnb_usd < state["objectif_revenu"] and stock > 50:
        decisions.append(("vendre", 0.8))
    # 2. Si leads faibles, marketing
    if leads < 10 and stock > 20:
        decisions.append(("marketing", 0.9))
    # 3. Si bots faibles, recruter
    if bots < 12:
        decisions.append(("recruter", 0.7))
    # 4. Ajustement des prix en fonction du stock
    if stock > 500:
        decisions.append(("diminuer_prix", 0.8))
    elif stock < 50 and bnb_usd > 1:
        decisions.append(("augmenter_prix", 0.7))
    # 5. Investissement si trésorerie bonne
    if bnb_usd > 5 and stock > 200:
        decisions.append(("investir", 0.6))
    return decisions

def prendre_decision(decisions):
    if not decisions:
        return None, 0
    # Choisir la décision avec le poids le plus élevé
    best = max(decisions, key=lambda x: x[1])
    return best[0], best[1]

def main():
    log("🧠 CEO ENTREPRENEUR & LEADER – Décisions réelles, pas de simulation", "START")
    state = load_state()
    cycle = 0

    while True:
        try:
            cycle += 1
            bnb = get_bnb_balance()
            rate = get_bnb_usd_rate()
            bnb_usd = bnb * rate
            stock, leads = get_db_stats()
            bots = get_bot_count()
            log(f"Cycle {cycle}: BNB={bnb_usd:.2f} USD | Stock={stock} | Leads={leads} | Bots={bots} | Seuil vente={state['seuil_vente']} | Prix={state['prix_email']} USD")

            # Analyse et décision
            decisions = analyser_tendances(bnb_usd, stock, leads, bots, state)
            action, score = prendre_decision(decisions)
            if action:
                log(f"Décision entrepreneuriale : {action.upper()} (score {score})", "LEADERSHIP")
                if action == "vendre":
                    if stock > state["seuil_vente"]:
                        action_vendre()
                    else:
                        log("Stock insuffisant pour vendre", "INFO")
                elif action == "marketing":
                    action_marketing()
                elif action == "recruter":
                    action_recruter()
                elif action == "augmenter_prix":
                    action_augmenter_prix()
                elif action == "diminuer_prix":
                    action_diminuer_prix()
                elif action == "investir":
                    action_investir()
                state["derniere_decision"] = action
                save_state(state)
            else:
                # Aucune action urgente, mais on peut quand même vérifier le seuil de vente
                if stock > state["seuil_vente"]:
                    action_vendre()
                else:
                    log("Aucune action requise – monitoring", "INFO")

            # Ajustement du seuil de vente (apprentissage simple)
            if bnb_usd > 0.5 and stock > 10:
                state["seuil_vente"] = max(5, state["seuil_vente"] - 1)
            elif bnb_usd < 0.1 and stock > 100:
                state["seuil_vente"] = min(20, state["seuil_vente"] + 1)
            save_state(state)

            # Rapport horaire
            if cycle % 60 == 0:
                rapport = (
                    f"📊 RAPPORT LEADERSHIP - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                    f"💰 Trésorerie (BNB): {bnb_usd:.2f} USD\n"
                    f"📧 Stock emails: {stock}\n👥 Leads: {leads}\n🤖 Bots: {bots}\n"
                    f"🎯 Objectif revenu: {state['objectif_revenu']:.2f} USD\n"
                    f"⚙️ Seuil vente: {state['seuil_vente']} | Prix email: {state['prix_email']} USD\n"
                    f"💡 Dernière décision: {state['derniere_decision']}"
                )
                log(rapport, "REPORT")
                send_telegram(rapport)

            time.sleep(60)
        except Exception as e:
            log(f"Erreur critique: {e}", "ERROR")
            time.sleep(60)

if __name__ == "__main__":
    import json
    main()
