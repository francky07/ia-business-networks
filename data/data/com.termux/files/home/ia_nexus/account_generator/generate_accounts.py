#!/usr/bin/env python3
"""
Génère automatiquement des comptes (email jetables, et à terme réseaux sociaux)
Stocke dans la base SQLite partagée pour revente.
"""
import sqlite3
import os
import time
import random
import string
import requests
import json

DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")

def generate_temp_email():
    """Crée un email temporaire via GuerrillaMail API (sans inscription)"""
    try:
        r = requests.get("https://www.guerrillamail.com/ajax.php?f=get_email_address", timeout=10)
        data = r.json()
        email = data.get("email_addr")
        return email, None  # mot de passe non applicable
    except:
        # Fallback : génération locale
        local_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        domain = random.choice(["guerrillamail.com", "guerrillamailblock.com", "sharklasers.com"])
        return f"{local_part}@{domain}", None

def generate_social_account(site):
    """Simule la création d'un compte sur un réseau social (à adapter avec API réelles)"""
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    # Ici, on ne fait que générer des identifiants fictifs (pas de création réelle)
    return username, password

def store_account(acc_type, identifiant, password, prix=0.01):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO comptes (type, identifiant, mot_de_passe, date_creation, vendu, prix) VALUES (?,?,?,?,?,?)",
              (acc_type, identifiant, password, int(time.time()), 0, prix))
    conn.commit()
    conn.close()
    print(f"✅ {acc_type} créé : {identifiant}")

def main_cycle():
    print("🚀 Générateur de comptes actif (toutes les 2 minutes)")
    while True:
        # Générer 5 emails temporaires
        for _ in range(5):
            email, _ = generate_temp_email()
            if email:
                store_account("email_temporaire", email, "", prix=0.005)
        # Générer 2 comptes sociaux fictifs (à remplacer par de vraies inscriptions)
        for _ in range(2):
            username, pwd = generate_social_account("twitter")
            store_account("twitter_fictif", username, pwd, prix=0.02)
        time.sleep(120)

if __name__ == "__main__":
    main_cycle()
