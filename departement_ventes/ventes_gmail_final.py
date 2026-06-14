#!/usr/bin/env python3
import smtplib, ssl, random, asyncio, urllib.parse
from email.mime.text import MIMEText
from datetime import datetime

# === CONFIGURATION (à modifier une seule fois) ===
GMAIL_EMAIL = "votre_email@gmail.com"          # Remplacez
GMAIL_APP_PASSWORD = "le_mot_de_passe_app_16_lettres"  # Remplacez
PAYPAL_EMAIL = "faraseck@hotmail.fr"
# ================================================

queue = asyncio.Queue()
total_envoyes = 0

async def send_email(dest, subject, html):
    msg = MIMEText(html, 'html')
    msg['Subject'] = subject
    msg['From'] = GMAIL_EMAIL
    msg['To'] = dest
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[{datetime.now()}] Erreur Gmail: {e}")
        return False

async def worker(wid):
    global total_envoyes
    while True:
        p = await queue.get()
        montant = round(random.uniform(5, 15), 2)
        lien = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&amount={montant}&currency_code=EUR&item_name=emails"
        html = f"Bonjour {p['nom']},<br>Prix: {montant} EUR<br><a href='{lien}'>Payer</a>"
        if await send_email(p['email'], "Offre emails", html):
            total_envoyes += 1
            print(f"✅ Worker {wid} -> {p['email']} (total {total_envoyes})")
        queue.task_done()
        await asyncio.sleep(1)

async def feeder():
    prenoms = ["Jean","Marie","Paul","Sophie","Lucas","Emma"]
    noms = ["Dupont","Martin","Durand","Petit"]
    while True:
        for _ in range(random.randint(5, 20)):
            nom = f"{random.choice(prenoms)} {random.choice(noms)}"
            email = f"client{random.randint(1,9999)}@mail.com"
            await queue.put({"nom": nom, "email": email})
        print(f"📥 {queue.qsize()} prospects en file")
        await asyncio.sleep(30)

async def main():
    asyncio.create_task(feeder())
    for i in range(20):  # 20 workers suffisent
        asyncio.create_task(worker(i))
    while True:
        await asyncio.sleep(60)
        print(f"📊 Total emails envoyés: {total_envoyes}")

if __name__ == "__main__":
    asyncio.run(main())
