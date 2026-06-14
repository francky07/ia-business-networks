#!/usr/bin/env python3
import imaplib
import email
import re
import os
import time
from email.header import decode_header

# Configuration (à adapter si nécessaire)
IMAP_SERVER = "imap.gmail.com"
EMAIL_ACCOUNT = os.getenv("PAYPAL_EMAIL", "seckndananeuh@gmail.com")
EMAIL_PASSWORD = os.getenv("PAYPAL_IMAP_PASSWORD")

if not EMAIL_PASSWORD:
    print("❌ Variable PAYPAL_IMAP_PASSWORD non définie dans .env_ia_business")
    exit(1)

def get_latest_paypal_code():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")
        # Recherche des emails non lus de PayPal (plus large)
        status, messages = mail.search(None, '(UNSEEN FROM "paypal@mail.com")')
        mail_ids = messages[0].split()
        if not mail_ids:
            print("Aucun nouvel email PayPal trouvé.")
            return None
        latest_id = mail_ids[-1]
        res, msg_data = mail.fetch(latest_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()
                # Recherche d'un code à 6 chiffres
                codes = re.findall(r'\b\d{6}\b', body)
                if codes:
                    print(f"✅ Code PayPal : {codes[0]}")
                    return codes[0]
        mail.logout()
    except Exception as e:
        print(f"Erreur : {e}")
    return None

if __name__ == "__main__":
    get_latest_paypal_code()
