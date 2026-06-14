#!/usr/bin/env python3
import sqlite3, smtplib, os, time
from email.mime.text import MIMEText
DB = os.path.expanduser("~/ia_shared/db/nexus.db")
# Config SMTP (Brevo)
def send_newsletter():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT email FROM leads WHERE contacte=0 LIMIT 10")
    leads = c.fetchall()
    for lead in leads:
        # Envoyer un email
        pass
    conn.close()
while True:
    send_newsletter()
    time.sleep(86400)
