#!/usr/bin/env python3
"""
DÉPARTEMENT VENTES – INDÉPENDANCE TOTALE
+ Prospectus automatique (génération illimitée)
+ Envoi massif (SMTP multi-comptes)
+ Paiements PayPal (API + fallback)
+ Livraison instantanée
+ Auto-réparation
"""

import asyncio
import json
import os
import random
import re
import smtplib
import ssl
import sys
import time
import urllib.parse
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from typing import Dict, List, Optional, Tuple

# ========= CONFIGURATION (à modifier une fois) =========
# PayPal – vous devez générer des clés LIVE sur developer.paypal.com
PAYPAL_CLIENT_ID = "VOTRE_CLIENT_ID_ICI"
PAYPAL_CLIENT_SECRET = "VOTRE_SECRET_ICI"
PAYPAL_MODE = "live"          # ou "sandbox" pour test

# Comptes SMTP (pour envoyer massivement sans être bloqué)
# Format : [("email1@domaine.com", "mot_de_passe"), ("email2", "mdp2"), ...]
SMTP_ACCOUNTS = [
    ("votre_email@gmail.com", "mot_de_passe_app"),
    # Ajoutez autant que nécessaire (jusqu'à 20 comptes recommandés)
]
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Quantités
NB_AGENTS = 200
NB_BOOSTERS = 100
PAIEMENT_CHECK_INTERVAL = 60   # secondes

# Fichiers
AGENCE_KEYS = os.path.expanduser("~/agence_kays/keys.json")
VENTES_DIR = os.path.expanduser("~/departement_ventes/ventes_en_cours")
LIVRAISONS_DIR = os.path.expanduser("~/departement_ventes/livraisons")
LOG_FILE = os.path.expanduser("~/departement_ventes/independance.log")
# =======================================================

# Files asynchrones
queue_normal = asyncio.Queue()
queue_haute = asyncio.Queue()
smtp_pool = asyncio.Queue()
stats = {"envoyes": 0, "payes": 0, "livres": 0, "erreurs": 0}
running = True

def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")

# ---------- PROSPECTION AUTOMATIQUE ----------
def generer_prospects(n: int = 10) -> List[Dict]:
    """Génère des prospects aléatoires (nom, email, entreprise, score)"""
    prenoms = ["Jean", "Marie", "Pierre", "Sophie", "Thomas", "Julie", "Nicolas", "Laura", "Lucas", "Emma"]
    noms = ["Dupont", "Martin", "Durand", "Lefebvre", "Moreau", "Simon", "Laurent", "Michel"]
    entreprises = ["TechCorp", "DataSys", "WebSolutions", "CloudNine", "SmartAI", "NetDyn", "InfoPlus"]
    domains = ["gmail.com", "yahoo.fr", "outlook.com", "protonmail.com", "entreprise.fr"]
    prospects = []
    for _ in range(n):
        prenom = random.choice(prenoms)
        nom_famille = random.choice(noms)
        email = f"{prenom.lower()}.{nom_famille.lower()}@{random.choice(domains)}"
        prospect = {
            "email": email,
            "nom": f"{prenom} {nom_famille}",
            "entreprise": random.choice(entreprises),
            "score": random.randint(20, 100),
            "date_creation": datetime.now().isoformat()
        }
        prospects.append(prospect)
    return prospects

# ---------- SMTP MULTI-COMPTES ----------
async def init_smtp_pool():
    for email, pwd in SMTP_ACCOUNTS:
        await smtp_pool.put((email, pwd))
    log(f"Pool SMTP initialisé avec {len(SMTP_ACCOUNTS)} comptes")

async def envoyer_email_smtp(destinataire: str, sujet: str, corps_html: str) -> bool:
    """Envoie un email en utilisant un compte du pool (rotation automatique)"""
    email_sender, password = await smtp_pool.get()
    try:
        msg = MIMEText(corps_html, 'html')
        msg['Subject'] = sujet
        msg['From'] = email_sender
        msg['To'] = destinataire
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(email_sender, password)
            server.send_message(msg)
        await asyncio.sleep(0.5)  # éviter throttling
        await smtp_pool.put((email_sender, password))
        return True
    except Exception as e:
        log(f"SMTP échec avec {email_sender} -> {e}")
        # Ne pas remettre le compte défaillant dans le pool tout de suite (on le retire temporairement)
        # Pour simplifier, on le remet mais il pourrait être blacklisté. 
        await smtp_pool.put((email_sender, password))
        return False

# ---------- PAYPAL (API + fallback) ----------
async def get_paypal_token() -> Optional[str]:
    """Obtenir un token OAuth2 via API PayPal (avec tentatives)"""
    import aiohttp
    url = f"https://api-m.paypal.com/v1/oauth2/token" if PAYPAL_MODE == "live" else "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}
    async with aiohttp.ClientSession() as session:
        for _ in range(3):
            try:
                async with session.post(url, headers=headers, data=data, ssl=False) as resp:
                    if resp.status == 200:
                        js = await resp.json()
                        return js.get("access_token")
                    else:
                        log(f"PayPal token erreur {resp.status}: {await resp.text()}")
            except Exception as e:
                log(f"PayPal token exception: {e}")
            await asyncio.sleep(2)
    return None

async def creer_lien_paypal_api(montant: float, description: str, custom_id: str) -> Optional[str]:
    """Crée une commande PayPal et retourne le lien d'approbation"""
    token = await get_paypal_token()
    if not token:
        # Fallback : lien classique sans API (mais alors pas de suivi auto)
        return generer_lien_classique(montant, description, custom_id)
    url = "https://api-m.paypal.com/v2/checkout/orders" if PAYPAL_MODE == "live" else "https://api-m.sandbox.paypal.com/v2/checkout/orders"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{"amount": {"currency_code": "EUR", "value": f"{montant:.2f}"}, "custom_id": custom_id}],
        "application_context": {"return_url": "https://exemple.com/retour", "cancel_url": "https://exemple.com/annuler"}
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload, ssl=False) as resp:
            if resp.status in (200, 201):
                data = await resp.json()
                for link in data.get("links", []):
                    if link.get("rel") == "approve":
                        return link.get("href")
            else:
                log(f"Erreur création commande: {resp.status} {await resp.text()}")
    return generer_lien_classique(montant, description, custom_id)

def generer_lien_classique(montant: float, description: str, custom_id: str) -> str:
    """Lien PayPal classique (fallback) – sans suivi automatique, mais l'utilisateur peut toujours payer"""
    params = {
        "cmd": "_xclick",
        "business": "faraseck@hotmail.fr",  # À changer par votre email marchand
        "amount": f"{montant:.2f}",
        "currency_code": "EUR",
        "item_name": description,
        "custom": custom_id,
        "no_shipping": "1"
    }
    return "https://www.paypal.com/cgi-bin/webscr?" + urllib.parse.urlencode(params)

async def verifier_paiements_api() -> List[Dict]:
    """Récupère les transactions récentes via l'API PayPal et retourne les commandes payées"""
    token = await get_paypal_token()
    if not token:
        return []
    url = "https://api-m.paypal.com/v1/reporting/transactions"
    # Date de début = maintenant - 1 jour
    start_date = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
    end_date = datetime.utcnow().isoformat() + "Z"
    params = {"start_date": start_date, "end_date": end_date, "fields": "all"}
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params, ssl=False) as resp:
            if resp.status == 200:
                data = await resp.json()
                # Analyser les transactions avec status = "COMPLETED"
                payes = []
                for tx in data.get("transaction_details", []):
                    if tx.get("transaction_status") == "C":
                        custom_id = tx.get("custom") or tx.get("transaction_info", {}).get("custom_id")
                        if custom_id:
                            payes.append({"custom_id": custom_id, "montant": tx.get("transaction_info", {}).get("amount")})
                return payes
            else:
                log(f"Erreur vérification paiements: {resp.status}")
    return []

# ---------- CORE : AGENTS & BOOSTERS ----------
async def agent_ventes(agent_id: int, queue: asyncio.Queue, booster: bool = False):
    """Agent ou booster qui envoie des emails de vente"""
    role = "BOOSTER" if booster else "AGENT"
    while running:
        prospect = await queue.get()
        try:
            # Générer lien PayPal unique
            custom_id = f"vente_{agent_id}_{int(time.time())}_{random.randint(1000,9999)}"
            montant = random.uniform(3.0, 15.0) if not booster else random.uniform(5.0, 25.0)
            description = f"Liste d'emails qualifiés (pack {random.choice(['startup','pro','premium'])}"
            lien = await creer_lien_paypal_api(montant, description, custom_id)
            
            # Préparer l'email
            nb_emails = await get_nb_emails_dispo()
            corps_html = f"""
            <html><body>
            <h2>Bonjour {prospect['nom']},</h2>
            <p>Nous avons actuellement <b>{nb_emails}</b> emails vérifiés et prêts à être utilisés.</p>
            <p>Offre spéciale : <b>{montant:.2f} EUR</b> pour le pack.</p>
            <p><a href='{lien}'>Cliquez ici pour acheter</a></p>
            <p>Après paiement, la liste vous sera livrée automatiquement.</p>
            </body></html>
            """
            sujet = f"Liste d'emails B2B – offre {prospect['entreprise']}"
            
            # Envoi via SMTP pool
            success = await envoyer_email_smtp(prospect['email'], sujet, corps_html)
            if success:
                stats["envoyes"] += 1
                # Sauvegarder la vente en attente
                sauvegarder_vente(prospect, custom_id, montant, lien)
                log(f"{role} {agent_id} -> envoyé à {prospect['email']} (custom {custom_id})")
            else:
                stats["erreurs"] += 1
        except Exception as e:
            log(f"Erreur agent {agent_id}: {e}")
            stats["erreurs"] += 1
        finally:
            queue.task_done()
            # Pause variable pour respecter limites
            await asyncio.sleep(1 if booster else 2)

def sauvegarder_vente(prospect: dict, custom_id: str, montant: float, lien: str):
    """Enregistre une vente en attente de paiement"""
    os.makedirs(VENTES_DIR, exist_ok=True)
    fichier = os.path.join(VENTES_DIR, f"{custom_id}.json")
    with open(fichier, "w") as f:
        json.dump({
            "prospect": prospect,
            "custom_id": custom_id,
            "montant": montant,
            "lien": lien,
            "date_envoi": datetime.now().isoformat(),
            "paye": False
        }, f, indent=2)

async def verifier_et_livrer():
    """Boucle qui vérifie les paiements et livre les emails automatiquement"""
    while running:
        await asyncio.sleep(PAIEMENT_CHECK_INTERVAL)
        # Vérifier via API
        payes = await verifier_paiements_api()
        for p in payes:
            custom_id = p["custom_id"]
            fichier = os.path.join(VENTES_DIR, f"{custom_id}.json")
            if not os.path.exists(fichier):
                continue
            with open(fichier, "r") as f:
                vente = json.load(f)
            if vente.get("paye"):
                continue
            # Marquer comme payé
            vente["paye"] = True
            vente["date_paiement"] = datetime.now().isoformat()
            with open(fichier, "w") as f:
                json.dump(vente, f, indent=2)
            stats["payes"] += 1
            # Livrer les emails
            await livrer_emails(vente)

async def livrer_emails(vente: dict):
    """Livraison : prend des emails depuis agence_kays et les envoie au client"""
    prospect = vente["prospect"]
    # Charger les emails disponibles
    if not os.path.exists(AGENCE_KEYS):
        log(f"ERREUR: {AGENCE_KEYS} manquant")
        return
    with open(AGENCE_KEYS, "r") as f:
        data = json.load(f)
    emails_a_vendre = data.get("emails", [])
    if not emails_a_vendre:
        log(f"Plus d'emails à vendre pour {prospect['email']}")
        return
    # Nombre d'emails à livrer (par exemple 100 ou tout si moins)
    lot = emails_a_vendre[:100] if len(emails_a_vendre) > 100 else emails_a_vendre[:]
    # Envoyer par email au client
    corps = f"Bonjour {prospect['nom']},\n\nVoici les {len(lot)} emails que vous avez achetés :\n\n" + "\n".join(lot)
    sujet = "Livraison de votre liste d'emails"
    await envoyer_email_smtp(prospect['email'], sujet, corps.replace('\n', '<br>'))
    # Mettre à jour le stock : enlever les emails livrés
    data["emails"] = emails_a_vendre[len(lot):]
    with open(AGENCE_KEYS, "w") as f:
        json.dump(data, f, indent=2)
    # Archiver
    os.makedirs(LIVRAISONS_DIR, exist_ok=True)
    with open(os.path.join(LIVRAISONS_DIR, f"livraison_{vente['custom_id']}.json"), "w") as f:
        json.dump(vente, f, indent=2)
    stats["livres"] += len(lot)
    log(f"Livré {len(lot)} emails à {prospect['email']} (stock restant: {len(data['emails'])})")

async def get_nb_emails_dispo() -> int:
    try:
        with open(AGENCE_KEYS, "r") as f:
            return len(json.load(f).get("emails", []))
    except:
        return 0

async def feed_prospects():
    """Alimente continuellement les files avec des prospects nouveaux"""
    while running:
        # Générer 5 à 20 nouveaux prospects à chaque cycle
        n = random.randint(5, 20)
        prospects = generer_prospects(n)
        for p in prospects:
            if p["score"] >= 70:
                await queue_haute.put(p)
            else:
                await queue_normal.put(p)
        log(f"Feed : ajouté {n} prospects (normal={queue_normal.qsize()}, haute={queue_haute.qsize()})")
        await asyncio.sleep(30)

async def monitor():
    """Affiche les stats périodiquement et redémarre si besoin"""
    while running:
        await asyncio.sleep(60)
        log(f"STATS: envoyés={stats['envoyes']}, payés={stats['payes']}, livrés={stats['livres']}, erreurs={stats['erreurs']}")
        # Auto-réparation : si trop d'erreurs, réinitialiser le pool SMTP ?
        if stats["erreurs"] > 50:
            log("Trop d'erreurs, réinitialisation du pool SMTP...")
            await init_smtp_pool()
            stats["erreurs"] = 0

async def main():
    global running
    log("Démarrage du département ventes autonome")
    await init_smtp_pool()
    # Lancer le feed
    asyncio.create_task(feed_prospects())
    # Lancer les agents
    for i in range(NB_AGENTS):
        asyncio.create_task(agent_ventes(i, queue_normal, booster=False))
    for i in range(NB_BOOSTERS):
        asyncio.create_task(agent_ventes(i, queue_haute, booster=True))
    # Lancer la vérification des paiements et la livraison
    asyncio.create_task(verifier_et_livrer())
    # Lancer le monitoring
    await monitor()

if __name__ == "__main__":
    # Vérifier les dépendances
    try:
        import aiohttp
    except ImportError:
        os.system("pip install aiohttp")
        import aiohttp
    try:
        import base64
    except:
        pass
    asyncio.run(main())
