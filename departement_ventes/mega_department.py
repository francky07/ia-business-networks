#!/usr/bin/env python3
"""
MEGA DÉPARTEMENT VENTES
200 agents + 100 booster pro (asynchrones, légers)
Fonctionne sur Termux avec asyncio (pas de threading lourd)
"""

import asyncio
import json
import os
import random
import time
import urllib.parse
import hashlib
from datetime import datetime
from typing import Dict, List, Optional

# ========= CONFIGURATION =========
NB_AGENTS = 200
NB_BOOSTERS = 100
PROSPECTS_FILE = os.path.expanduser("~/departement_ventes/prospects.csv")
AGENCE_KAYS_KEYS = os.path.expanduser("~/agence_kays/keys.json")
EMAIL_MARCHAND = "faraseck@hotmail.fr"   # Votre email PayPal
DEVISE = "EUR"
MONTANT_PAR_DEFAUT = 5.0

# Pour SMTP (Gmail) – à configurer une fois
SMTP_CONFIG = {
    "server": "smtp.gmail.com",
    "port": 587,
    "username": "votre_email@gmail.com",   # À remplacer
    "password": "votre_mot_de_passe_app"   # Mot de passe d'application
}
# =================================

# File de prospects (priorité normale et haute pour boosters)
queue_normal = asyncio.Queue()
queue_haute_priorite = asyncio.Queue()

stats = {
    "emails_envoyes": 0,
    "ventes_realisees": 0,
    "boosters_utilises": 0
}

def charger_prospects() -> List[Dict]:
    """Charge la liste des prospects depuis CSV"""
    if not os.path.exists(PROSPECTS_FILE):
        # Créer un exemple
        os.makedirs(os.path.dirname(PROSPECTS_FILE), exist_ok=True)
        with open(PROSPECTS_FILE, 'w') as f:
            f.write("email,nom,entreprise,score\nclient1@exemple.com,Jean,Acme,50\nclient2@exemple.com,Marie,Beta,80\n")
        print(f"[INFO] Fichier prospects créé : {PROSPECTS_FILE}. Remplissez-le.")
        return []
    import csv
    with open(PROSPECTS_FILE, 'r') as f:
        return list(csv.DictReader(f))

def generer_lien_paypal(prospect_email: str, montant: float, description: str) -> str:
    """Génère un lien PayPal classique (sans API)"""
    custom = hashlib.md5(f"{prospect_email}_{time.time()}".encode()).hexdigest()[:8]
    params = {
        "cmd": "_xclick",
        "business": EMAIL_MARCHAND,
        "amount": f"{montant:.2f}",
        "currency_code": DEVISE,
        "item_name": description,
        "custom": custom,
        "no_shipping": "1",
        "return": "https://votre-site.com/merci",
        "cancel_return": "https://votre-site.com/annule"
    }
    return "https://www.paypal.com/cgi-bin/webscr?" + urllib.parse.urlencode(params)

async def envoyer_email_async(destinataire: str, sujet: str, corps_html: str) -> bool:
    """Envoie un email de manière asynchrone (thread pool)"""
    # Pour éviter de bloquer l'event loop, on utilise asyncio.to_thread
    import smtplib
    from email.mime.text import MIMEText
    def _send():
        msg = MIMEText(corps_html, 'html')
        msg['Subject'] = sujet
        msg['From'] = SMTP_CONFIG['username']
        msg['To'] = destinataire
        try:
            with smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port']) as server:
                server.starttls()
                server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Erreur SMTP pour {destinataire}: {e}")
            return False
    return await asyncio.to_thread(_send)

async def agent(agent_id: int, queue: asyncio.Queue, booster_mode: bool = False):
    """Un agent ou booster pro qui traite des prospects"""
    role = "BOOSTER_PRO" if booster_mode else "AGENT"
    while True:
        prospect = await queue.get()
        try:
            print(f"[{role} #{agent_id}] Traite {prospect['email']} (score {prospect.get('score',0)})")
            # Simuler une petite latence (prospection, envoi email)
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Générer un lien personnalisé
            montant = MONTANT_PAR_DEFAUT + random.uniform(-1, 2)  # variation
            montant = max(1, round(montant, 2))
            lien = generer_lien_paypal(prospect['email'], montant, "Liste d'emails qualifiés")
            
            # Corps de l'email (HTML)
            corps = f"""
            <html>
            <body>
            <h2>Offre spéciale pour {prospect.get('nom', 'vous')}</h2>
            <p>Nous avons actuellement {await get_nb_emails_dispo()} emails qualifiés à vendre.</p>
            <p>Prix spécial : <b>{montant} {DEVISE}</b></p>
            <p><a href='{lien}'>Cliquez ici pour acheter immédiatement</a></p>
            <p>Après paiement, vous recevrez la liste par email.</p>
            </body>
            </html>
            """
            sujet = f"Liste d'emails B2B – offre personnalisée {prospect.get('entreprise', '')}"
            
            # Envoi effectif
            success = await envoyer_email_async(prospect['email'], sujet, corps)
            if success:
                stats["emails_envoyes"] += 1
                if booster_mode:
                    stats["boosters_utilises"] += 1
                print(f"✅ [{role} #{agent_id}] Email envoyé à {prospect['email']}")
            else:
                print(f"❌ [{role} #{agent_id}] Échec envoi à {prospect['email']}")
                
            # Si booster, on traite plus vite ?
            if booster_mode:
                await asyncio.sleep(0.2)  # boosté
        except Exception as e:
            print(f"Erreur agent {agent_id}: {e}")
        finally:
            queue.task_done()

async def get_nb_emails_dispo() -> int:
    """Retourne le nombre d'emails disponibles dans l'agence Kays"""
    try:
        with open(AGENCE_KAYS_KEYS, 'r') as f:
            data = json.load(f)
            return len(data.get("emails", []))
    except:
        return 0

async def feeder():
    """Remplit la file de prospects en continu (simule l'arrivée de nouveaux prospects)"""
    prospects = charger_prospects()
    if not prospects:
        print("Aucun prospect trouvé. Attente de fichier...")
        while True:
            await asyncio.sleep(10)
            prospects = charger_prospects()
            if prospects:
                break
    # On répartit selon le score : score élevé -> queue haute priorité (boosters)
    for p in prospects:
        score = int(p.get("score", 50))
        if score >= 70:
            await queue_haute_priorite.put(p)
        else:
            await queue_normal.put(p)
    print(f"Feed initial : {queue_normal.qsize()} normaux, {queue_haute_priorite.qsize()} haute priorité")
    # Puis périodiquement, on recharge (simule nouveaux prospects)
    while True:
        await asyncio.sleep(30)
        nouveaux = charger_prospects()
        # Éviter les doublons basique (par email)
        existing_emails = set()
        # On pourrait maintenir un set, mais simplifions
        for p in nouveaux:
            if random.random() < 0.3:  # 30% de chance d'ajouter un nouveau
                score = int(p.get("score", 50))
                if score >= 70:
                    await queue_haute_priorite.put(p)
                else:
                    await queue_normal.put(p)
        print(f"[FEEDER] Nouvelles entrées. Files : normal={queue_normal.qsize()}, prioritaire={queue_haute_priorite.qsize()}")

async def afficher_stats():
    """Affiche les statistiques toutes les 10 secondes"""
    while True:
        await asyncio.sleep(10)
        print("\n" + "="*50)
        print(f"📊 STATS : Emails envoyés = {stats['emails_envoyes']}, Ventes = {stats['ventes_realisees']}, Boosters actifs = {stats['boosters_utilises']}")
        print(f"📨 Files : normal={queue_normal.qsize()}, prioritaire={queue_haute_priorite.qsize()}")
        print(f"📧 Emails dispo en agence : {await get_nb_emails_dispo()}")
        print("="*50)

async def main():
    # Démarrer le feeder
    asyncio.create_task(feeder())
    # Démarrer les agents normaux
    for i in range(NB_AGENTS):
        asyncio.create_task(agent(i, queue_normal, booster_mode=False))
    # Démarrer les boosters pro (ils piochent dans la file haute priorité)
    for i in range(NB_BOOSTERS):
        asyncio.create_task(agent(i, queue_haute_priorite, booster_mode=True))
    # Lancer l'affichage des stats
    await afficher_stats()

if __name__ == "__main__":
    print(f"🚀 Lancement du département ventes avec {NB_AGENTS} agents et {NB_BOOSTERS} boosters pro")
    asyncio.run(main())
