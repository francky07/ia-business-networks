#!/usr/bin/env python3
"""
Agent de prospection autonome – cherche des missions rémunérées et postule.
"""
import requests
import re
import time
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
PAYPAL_EMAIL = "faraseck@hotmail.fr"

# Configuration SMTP (Brevo)
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USER = "seckndananeuh@gmail.com"
SMTP_PASSWORD = "xsmtpsib-9364b75a7aa91f2040c5ccc04b90c01224b070f1efc4b97d5c21a896ec6e8527-BheO7lIdmm52XdF4"

def send_email(dest, sujet, corps):
    msg = MIMEText(corps, 'plain')
    msg['Subject'] = sujet
    msg['From'] = SMTP_USER
    msg['To'] = dest
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASSWORD)
            s.send_message(msg)
        return True
    except:
        return False

def scrape_offres():
    """Exemple : scraping de la page d'offres Freelance-info"""
    offres = []
    url = "https://www.freelance-info.fr/annonces"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for article in soup.select(".annonce")[:10]:
            titre = article.select_one(".titre").text if article.select_one(".titre") else "Sans titre"
            budget = article.select_one(".budget").text if article.select_one(".budget") else "0€"
            lien = article.select_one("a")['href'] if article.select_one("a") else ""
            offres.append({"titre": titre, "budget": budget, "lien": lien})
    except Exception as e:
        print(f"Erreur scraping: {e}")
    return offres

def qualifier(offre):
    score = 0
    if "IA" in offre["titre"] or "automatisation" in offre["titre"]:
        score += 30
    if "€" in offre["budget"] and int(re.findall(r'\d+', offre["budget"])[0]) > 100:
        score += 40
    return score

def postuler(offre, score):
    if score < 50:
        return
    sujet = f"Candidature pour {offre['titre']}"
    corps = f"Bonjour,\n\nNotre IA peut réaliser ce projet pour {offre['budget']}.\n\nLien PayPal pour payer : https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&amount={0.01*score}&currency_code=USD\n\nCordialement."
    # Envoi à un destinataire de test (à remplacer par le contact réel)
    send_email("faraseck@hotmail.fr", sujet, corps)
    print(f"Candidature envoyée pour {offre['titre']} (score {score})")

def main():
    print("🚀 Agent de prospection autonome démarré")
    while True:
        offres = scrape_offres()
        for offre in offres:
            score = qualifier(offre)
            if score > 0:
                postuler(offre, score)
        time.sleep(3600)  # toutes les heures

if __name__ == "__main__":
    main()
