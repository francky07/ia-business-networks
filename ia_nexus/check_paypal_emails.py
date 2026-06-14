#!/usr/bin/env python3
import imaplib, email, time, sqlite3, os
from email.header import decode_header

IMAP_SERVER = "imap.gmail.com"  # ou hotmail/outlook
EMAIL = "faraseck@hotmail.fr"
PASSWORD = "ton_mot_de_passe"   # utiliser un mot de passe d'application

DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")

def connect_imap():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")
    return mail

def mark_as_read(mail, uid):
    mail.store(uid, '+FLAGS', '\\Seen')

def process_payment(email_body):
    # Extraire le montant et l'email du client (personnaliser selon PayPal)
    # Exemple simplifié : rechercher "amount" et "payer_email"
    import re
    amount = re.search(r'amount=([\d.]+)', email_body)
    payer = re.search(r'payer_email=([\w\.@]+)', email_body)
    if amount and payer:
        # Marquer les emails correspondants comme livrés dans la base
        conn = sqlite3.connect(DB_PATH)
        conn.execute("UPDATE emails SET vendu=2 WHERE vendu=1")  # 2 = livré
        conn.commit()
        conn.close()
        print(f"Paiement reçu de {payer.group(1)} pour {amount.group(1)} USD")

def main():
    mail = connect_imap()
    # Rechercher les emails non lus de PayPal
    result, uids = mail.uid('search', None, '(UNSEEN FROM "paypal@mail.com")')
    for uid in uids[0].split():
        result, data = mail.uid('fetch', uid, '(RFC822)')
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()
        process_payment(body)
        mark_as_read(mail, uid)
    mail.close()
    mail.logout()

if __name__ == "__main__":
    main()
