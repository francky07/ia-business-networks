#!/usr/bin/env python3
"""
CEO GÉNIE – Entrepreneur & Leader
Décisions réelles, pas de simulation. Anticipe, s'adapte, communique.
"""
import time, os, json, sqlite3, subprocess, requests, smtplib, ssl
from datetime import datetime
from email.mime.text import MIMEText
from web3 import Web3

# ==================== CONFIGURATION ====================
DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
LOG_FILE = os.path.expanduser("~/ceo_genie.log")
STATE_FILE = os.path.expanduser("~/ceo_genie_state.json")

# SMTP Brevo (pour les emails marketing)
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
        "objectif_revenu": 10.0,
        "budget_marketing": 5.0,
        "derniere_action": "",
        "historique_actions": []
    }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def send_telegram(msg):
    token = get_env("TELEGRAM_BOT_TOKEN")
    chat_id = get_env("TELEGRAM_CHAT_ID")
    if token and chat_id and token != "VOTRE_TOKEN":
        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": msg}, timeout=5)
            log("Notification Telegram envoyée", "ACTION")
        except Exception as e:
            log(f"Erreur Telegram: {e}", "ERROR")

# ==================== COLLECTE DE DONNÉES ====================
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
    sessions = [l for l in out.splitlines() if "ceo_genie" not in l and l]
    return len(sessions)

# ==================== ACTIONS RÉELLES ====================
def action_vendre():
    """Déclenche la vente des emails en stock"""
    log("ACTION: Vente massive déclenchée", "ACTION")
    subprocess.run(["python", os.path.expanduser("~/departement_ventes/sell_emails_paypal.py")])

def action_marketing():
    """Envoie un email à tous les leads non contactés (max 50)"""
    log("ACTION: Campagne marketing par email", "ACTION")
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT email FROM leads WHERE contacte=0 LIMIT 50")
        leads = c.fetchall()
        if not leads:
            log("Aucun lead à contacter", "INFO")
            return
        subject = "Offre spéciale IA Business – Liste d'emails qualifiés"
        body = f"""<html><body><h2>Bonjour,</h2><p>Notre IA a généré une liste d'emails vérifiés.</p><p>Prix : {load_state()['prix_email']} USD/email. <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&amount=1.00&currency_code=USD">Acheter maintenant</a></p><p>Cordialement,<br>IA Business</p></body></html>"""
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
    """Lance un nouveau booster (agent de surveillance)"""
    log("ACTION: Recrutement d'un booster", "ACTION")
    subprocess.run(["tmux", "new-session", "-d", "-s", f"recruit_{int(time.time())}", "python ~/ia_booster_agence.py"], shell=True)
    send_telegram("🤖 Nouveau booster recruté.")

def action_augmenter_prix():
    """Augmente le prix unitaire des emails de 0.005 USD"""
    state = load_state()
    new_price = round(state["prix_email"] + 0.005, 3)
    state["prix_email"] = new_price
    save_state(state)
    # Modifier le script de vente pour utiliser le nouveau prix
    subprocess.run(f"sed -i 's/montant = nb \\* [0-9.]*/montant = nb * {new_price}/' ~/departement_ventes/sell_emails_paypal.py", shell=True)
    log(f"Prix des emails augmenté à {new_price} USD", "ACTION")
    send_telegram(f"💰 Prix des emails augmenté à {new_price} USD.")

def action_diminuer_prix():
    """Diminue le prix unitaire des emails de 0.005 USD (minimum 0.002)"""
    state = load_state()
    new_price = max(0.002, state["prix_email"] - 0.005)
    state["prix_email"] = round(new_price, 3)
    save_state(state)
    subprocess.run(f"sed -i 's/montant = nb \\* [0-9.]*/montant = nb * {new_price}/' ~/departement_ventes/sell_emails_paypal.py", shell=True)
    log(f"Prix des emails diminué à {new_price} USD", "ACTION")
    send_telegram(f"💰 Prix des emails diminué à {new_price} USD.")

def action_investir():
    """Investit dans l'infrastructure : lance un booster supplémentaire et améliore la productivité (simulation d'effet)"""
    log("ACTION: Investissement dans l'infrastructure", "ACTION")
    # Lance deux boosters pour renforcer
    for _ in range(2):
        subprocess.run(["tmux", "new-session", "-d", "-s", f"invest_{int(time.time())}", "python ~/ia_booster_agence.py"], shell=True)
    send_telegram("🚀 Investissement réalisé : deux boosters supplémentaires actifs.")

# ==================== STRATÉGIE ET LEADERSHIP ====================
def analyser_opportunites(bnb_usd, stock, leads, bots, state):
    """Analyse multi-critères pour prendre des décisions stratégiques"""
    actions = []
    # 1. Vente : si stock élevé ou si objectif de revenu non atteint
    if stock > state["seuil_vente"]:
        actions.append(("vendre", 1.0))
    elif stock > 20 and bnb_usd < state["objectif_revenu"]:
        actions.append(("vendre", 0.8))
    # 2. Marketing : si leads faibles mais stock suffisant
    if leads < 15 and stock > 30:
        actions.append(("marketing", 0.9))
    # 3. Recrutement : si bots insuffisants
    if bots < 12:
        actions.append(("recruter", 0.7))
    # 4. Ajustement des prix : en fonction du stock
    if stock > 500:
        actions.append(("diminuer_prix", 0.9))
    elif stock < 50 and bnb_usd > 1:
        actions.append(("augmenter_prix", 0.8))
    # 5. Investissement : si trésorerie bonne et stock important
    if bnb_usd > 5 and stock > 200:
        actions.append(("investir", 0.7))
    return actions

def prendre_decision(actions):
    if not actions:
        return None
    # Choisir l'action avec le score le plus élevé (priorité)
    best = max(actions, key=lambda x: x[1])
    return best[0]

def main():
    log("🧠 CEO GÉNIE – Entrepreneur & Leader (décisions réelles)", "START")
    state = load_state()
    cycle = 0
    last_report = 0

    while True:
        try:
            cycle += 1
            bnb = get_bnb_balance()
            rate = get_bnb_usd_rate()
            bnb_usd = bnb * rate
            stock, leads = get_db_stats()
            bots = get_bot_count()
            log(f"Cycle {cycle}: BNB={bnb_usd:.2f} USD | Stock={stock} | Leads={leads} | Bots={bots} | Prix={state['prix_email']} USD")

            # Analyse et décision
            actions = analyser_opportunites(bnb_usd, stock, leads, bots, state)
            action = prendre_decision(actions)
            if action:
                log(f"DÉCISION STRATÉGIQUE : {action.upper()}", "LEADERSHIP")
                if action == "vendre":
                    action_vendre()
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
                state["derniere_action"] = action
                state["historique_actions"].append({"time": time.time(), "action": action})
                if len(state["historique_actions"]) > 100:
                    state["historique_actions"] = state["historique_actions"][-100:]
                save_state(state)
            else:
                # Si aucune action prioritaire, on peut quand même vendre si le stock dépasse le seuil
                if stock > state["seuil_vente"]:
                    action_vendre()
                else:
                    log("Aucune action urgente – monitoring", "INFO")

            # Ajustement adaptatif du seuil de vente (apprentissage simple)
            if bnb_usd > 1 and stock > 10:
                state["seuil_vente"] = max(5, state["seuil_vente"] - 1)
                log(f"Seuil de vente baissé à {state['seuil_vente']} (bonne performance)", "APPRENTISSAGE")
            elif bnb_usd < 0.1 and stock > 100:
                state["seuil_vente"] = min(20, state["seuil_vente"] + 1)
                log(f"Seuil de vente augmenté à {state['seuil_vente']} (faible rentabilité)", "APPRENTISSAGE")
            save_state(state)

            # Rapport horaire (toutes les 60 minutes)
            now = time.time()
            if now - last_report >= 3600:
                rapport = (
                    f"📊 RAPPORT DU GÉNIE - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                    f"💰 Trésorerie (BNB): {bnb_usd:.2f} USD\n"
                    f"📧 Stock emails: {stock}\n👥 Leads: {leads}\n🤖 Bots: {bots}\n"
                    f"🎯 Objectif revenu: {state['objectif_revenu']:.2f} USD\n"
                    f"⚙️ Seuil vente: {state['seuil_vente']} | Prix email: {state['prix_email']} USD\n"
                    f"💡 Dernière action: {state['derniere_action']}"
                )
                log(rapport, "REPORT")
                send_telegram(rapport)
                last_report = now

            time.sleep(60)
        except Exception as e:
            log(f"Erreur critique: {e}", "ERROR")
            time.sleep(60)

if __name__ == "__main__":
    main()
