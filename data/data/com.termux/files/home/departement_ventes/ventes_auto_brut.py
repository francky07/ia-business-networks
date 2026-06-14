#!/usr/bin/env python3
import os, asyncio, json, random, time, urllib.parse, smtplib, ssl
from email.mime.text import MIMEText
from datetime import datetime

# === IDENTIFIANTS DIRECTS (insécurisés) ===
PAYPAL_CLIENT_ID = "AWtfyaIH1TG63ijQjFO40fapigxovoqoUz2_8iWU1-8qSlEarr2cvkp8iMBYZJnlcx5SYirhr1Tj47Uv"
PAYPAL_CLIENT_SECRET = "EKIwuxjzkqWkdLfmmiYt3lVSs_HEuEH_8H-14kBSj1OM-Fb9I82VsgPYymmwHOaVcD6jkdMg5-Jv-JKh"
PAYPAL_MODE = "sandbox"
SMTP_EMAIL = "faraseck@hotmail.fr"
SMTP_PASSWORD = "Saint Louis65#"
# ========================================

NB_AGENTS = 200
NB_BOOSTERS = 100
AGENCE_KEYS = os.path.expanduser("~/agence_kays/keys.json")
queue_normal = asyncio.Queue()
queue_haute = asyncio.Queue()
stats = {"envoyes": 0}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

async def envoyer_email(dest, sujet, corps_html):
    msg = MIMEText(corps_html, 'html')
    msg['Subject'] = sujet
    msg['From'] = SMTP_EMAIL
    msg['To'] = dest
    try:
        # Hotmail/Outlook SMTP
        with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        log(f"SMTP erreur: {e}")
        return False

async def get_paypal_token():
    import aiohttp, base64
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as resp:
            if resp.status == 200:
                js = await resp.json()
                return js.get("access_token")
            log(f"PayPal token error {resp.status}: {await resp.text()}")
    return None

async def creer_lien_paypal(montant, description, custom_id):
    token = await get_paypal_token()
    if not token:
        # Fallback lien classique
        params = {
            "cmd": "_xclick",
            "business": SMTP_EMAIL,
            "amount": f"{montant:.2f}",
            "currency_code": "EUR",
            "item_name": description,
            "custom": custom_id
        }
        return "https://www.paypal.com/cgi-bin/webscr?" + urllib.parse.urlencode(params)
    url = "https://api-m.sandbox.paypal.com/v2/checkout/orders"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{"amount": {"currency_code": "EUR", "value": f"{montant:.2f}"}, "custom_id": custom_id}],
        "application_context": {"return_url": "https://example.com/return", "cancel_url": "https://example.com/cancel"}
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status in (200, 201):
                data = await resp.json()
                for link in data.get("links", []):
                    if link.get("rel") == "approve":
                        return link.get("href")
    return None

async def agent(agent_id, queue, booster=False):
    role = "BOOSTER" if booster else "AGENT"
    while True:
        prospect = await queue.get()
        try:
            custom = f"{agent_id}_{int(time.time())}_{random.randint(1000,9999)}"
            montant = random.uniform(5, 15)
            lien = await creer_lien_paypal(montant, "Pack emails qualifiés", custom)
            # Nombre d'emails dispo
            try:
                with open(AGENCE_KEYS, 'r') as f:
                    nb = len(json.load(f).get("emails", []))
            except:
                nb = 0
            corps = f"""
            Bonjour {prospect['nom']},<br>
            Nous avons {nb} emails vérifiés.<br>
            Prix : {montant:.2f} EUR<br>
            <a href='{lien}'>Cliquez pour payer</a>
            """
            ok = await envoyer_email(prospect['email'], "Offre spéciale", corps)
            if ok:
                stats["envoyes"] += 1
                log(f"{role} {agent_id} -> envoyé à {prospect['email']}")
        except Exception as e:
            log(f"Erreur agent {agent_id}: {e}")
        finally:
            queue.task_done()
            await asyncio.sleep(0.5 if booster else 1.5)

async def feed():
    # Génération continue de prospects fictifs
    prenoms = ["Jean", "Marie", "Pierre", "Sophie", "Thomas", "Julie"]
    noms = ["Dupont", "Martin", "Durand"]
    while True:
        n = random.randint(5, 20)
        for _ in range(n):
            prospect = {
                "nom": f"{random.choice(prenoms)} {random.choice(noms)}",
                "email": f"client{random.randint(1,9999)}@mail.com",
                "score": random.randint(0, 100)
            }
            if prospect["score"] > 70:
                await queue_haute.put(prospect)
            else:
                await queue_normal.put(prospect)
        log(f"Feed: ajouté {n} prospects (norm={queue_normal.qsize()}, haute={queue_haute.qsize()})")
        await asyncio.sleep(30)

async def main():
    log("Démarrage département ventes (modèle public)")
    asyncio.create_task(feed())
    for i in range(NB_AGENTS):
        asyncio.create_task(agent(i, queue_normal, booster=False))
    for i in range(NB_BOOSTERS):
        asyncio.create_task(agent(i, queue_haute, booster=True))
    while True:
        await asyncio.sleep(60)
        log(f"Stats: {stats['envoyes']} emails envoyés")

if __name__ == "__main__":
    asyncio.run(main())
