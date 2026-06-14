#!/usr/bin/env python3
import asyncio, smtplib, ssl, random, urllib.parse, os
from email.mime.text import MIMEText
from datetime import datetime

with open(os.path.expanduser("~/.secrets/smtp_ai.conf")) as f:
    cfg = {}
    for line in f:
        if '=' in line and not line.startswith('#'):
            k, v = line.strip().split('=', 1)
            cfg[k] = v.strip('"')

SMTP_HOST, SMTP_PORT = cfg['SMTP_SERVER'], int(cfg['SMTP_PORT'])
SMTP_USER, SMTP_PASS = cfg['SMTP_USER'], cfg['SMTP_PASSWORD']
PAYPAL_EMAIL = cfg['PAYPAL_EMAIL']

queue = asyncio.Queue()
sent = 0

async def send(to, sub, html):
    msg = MIMEText(html, 'html')
    msg['Subject'], msg['From'], msg['To'] = sub, SMTP_USER, to
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls(context=ctx)
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        return True
    except Exception as e:
        print(f"[{datetime.now()}] Erreur: {e}")
        return False

async def worker(wid):
    global sent
    while True:
        p = await queue.get()
        montant = round(random.uniform(5, 15), 2)
        link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&amount={montant}&currency_code=EUR"
        html = f"Bonjour {p['nom']},<br>Prix: {montant} €<br><a href='{link}'>Payer</a>"
        if await send(p['email'], "Offre", html):
            sent += 1
            print(f"✅ {wid} -> {p['email']} (total {sent})")
        queue.task_done()
        await asyncio.sleep(1)

async def feeder():
    prenoms = ["Jean","Marie","Paul","Sophie","Lucas","Emma"]
    noms = ["Dupont","Martin","Durand","Petit"]
    while True:
        for _ in range(random.randint(5, 20)):
            await queue.put({"nom": f"{random.choice(prenoms)} {random.choice(noms)}", "email": f"client{random.randint(1,9999)}@mail.com"})
        print(f"📥 {queue.qsize()} prospects")
        await asyncio.sleep(30)

async def main():
    asyncio.create_task(feeder())
    for i in range(20):
        asyncio.create_task(worker(i))
    while True:
        await asyncio.sleep(60)
        print(f"📊 Envoyés: {sent}")

asyncio.run(main())
