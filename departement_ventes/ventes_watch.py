#!/usr/bin/env python3
import smtplib, ssl, random, asyncio, urllib.parse
from email.mime.text import MIMEText
from datetime import datetime

# === IDENTIFIANTS À METTRE À JOUR APRÈS CE TEST ===
SMTP_HOST = "smtp.ai-net.com"
SMTP_PORT = 587
SMTP_USER = "votre_utilisateur"          # remplacez
SMTP_PASS = "olpf mbke lrzn xkmw"        # remplacez
PAYPAL_EMAIL = "faraseck@hotmail.fr"

queue = asyncio.Queue()
stats = 0

async def send_email(to, subject, html):
    msg = MIMEText(html, 'html')
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = to
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls(context=context)
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        return True
    except Exception as e:
        print(f"[{datetime.now()}] SMTP error: {e}")
        return False

async def worker(wid):
    global stats
    while True:
        p = await queue.get()
        montant = round(random.uniform(5, 15), 2)
        lien = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&amount={montant}&currency_code=EUR&item_name=emails"
        html = f"Bonjour {p['nom']},<br>Prix: {montant} EUR<br><a href='{lien}'>Payer</a>"
        if await send_email(p['email'], "Offre", html):
            stats += 1
            print(f"✅ Agent {wid} -> {p['email']} (total {stats})")
        queue.task_done()
        await asyncio.sleep(1)

async def feeder():
    prenoms = ["Jean","Marie","Paul","Sophie"]
    noms = ["Dupont","Martin"]
    while True:
        for _ in range(random.randint(5,20)):
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
        print(f"📊 Total emails envoyés: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
