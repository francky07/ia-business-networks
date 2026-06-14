#!/usr/bin/env python3
import asyncio, smtplib, ssl, random, urllib.parse, os
from email.mime.text import MIMEText
from datetime import datetime

# Lire la configuration
config = {}
with open(os.path.expanduser("~/.secrets/smtp_ai.conf")) as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            k, v = line.strip().split('=', 1)
            config[k] = v.strip('"')

SMTP_SERVER = config['SMTP_SERVER']
SMTP_PORT = int(config['SMTP_PORT'])
SMTP_USER = config['SMTP_USER']
SMTP_PASSWORD = config['SMTP_PASSWORD']
PAYPAL_EMAIL = config['PAYPAL_EMAIL']

queue = asyncio.Queue()
total_envoyes = 0

async def send_email(dest, sujet, html):
    msg = MIMEText(html, 'html')
    msg['Subject'] = sujet
    msg['From'] = SMTP_USER
    msg['To'] = dest
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
            s.starttls(context=context)
            s.login(SMTP_USER, SMTP_PASSWORD)
            s.send_message(msg)
        return True
    except Exception as e:
        print(f"[{datetime.now()}] Erreur SMTP: {e}")
        return False

async def worker(wid):
    global total_envoyes
    while True:
        p = await queue.get()
        montant = round(random.uniform(5, 15), 2)
        lien = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&amount={montant}&currency_code=EUR"
        html = f"Bonjour {p['nom']},<br>Prix: {montant} EUR<br><a href='{lien}'>Payer</a>"
        if await send_email(p['email'], "Offre", html):
            total_envoyes += 1
            print(f"✅ Worker {wid} -> {p['email']} (total {total_envoyes})")
        queue.task_done()
        await asyncio.sleep(1)

async def feeder():
    prenoms = ["Jean","Marie","Paul","Sophie"]
    noms = ["Dupont","Martin"]
    while True:
        for _ in range(random.randint(5,20)):
            await queue.put({"nom": f"{random.choice(prenoms)} {random.choice(noms)}", "email": f"client{random.randint(1,9999)}@mail.com"})
        print(f"📥 {queue.qsize()} prospects")
        await asyncio.sleep(30)

async def main():
    asyncio.create_task(feeder())
    for i in range(20):
        asyncio.create_task(worker(i))
    while True:
        await asyncio.sleep(60)
        print(f"📊 Emails envoyés: {total_envoyes}")

if __name__ == "__main__":
    asyncio.run(main())
