#!/usr/bin/env python3
"""
Département ventes – autonome (sans API PayPal)
Génère un lien de paiement PayPal standard, archive les emails vendus.
"""

import json
import os
import shutil
from datetime import datetime

# CONFIGURATION (à modifier une seule fois)
EMAIL_MARCHAND = "faraseck@hotmail.fr"   # Votre email PayPal qui recevra l'argent
DEVISE = "EUR"                            # ou USD, GBP...
OBJET = "Achat liste emails qualifiés"

def get_emails():
    """Récupère la liste des emails depuis agence_kays/keys.json"""
    fichier = os.path.expanduser("~/agence_kays/keys.json")
    if not os.path.exists(fichier):
        print("❌ Fichier agence_kays/keys.json introuvable.")
        return []
    with open(fichier, 'r') as f:
        data = json.load(f)
    return data.get("emails", [])

def generer_lien_paypal(montant, description):
    """Construit un lien PayPal standard (sans API)"""
    import urllib.parse
    params = {
        "cmd": "_xclick",
        "business": EMAIL_MARCHAND,
        "amount": str(montant),
        "currency_code": DEVISE,
        "item_name": description,
        "no_shipping": "1",
        "return": "https://example.com/merci",
        "cancel_return": "https://example.com/annule"
    }
    base_url = "https://www.paypal.com/cgi-bin/webscr"
    return base_url + "?" + urllib.parse.urlencode(params)

def archiver_emails(emails):
    """Archive les emails vendus et vide la liste principale"""
    dossier_archive = os.path.expanduser("~/departement_ventes/archives")
    os.makedirs(dossier_archive, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fichier_archive = os.path.join(dossier_archive, f"vente_{timestamp}.json")
    with open(fichier_archive, 'w') as f:
        json.dump({"date": timestamp, "emails": emails}, f, indent=2)
    
    # Vider la liste dans keys.json
    fichier_keys = os.path.expanduser("~/agence_kays/keys.json")
    with open(fichier_keys, 'r') as f:
        data = json.load(f)
    data["emails"] = []
    with open(fichier_keys, 'w') as f:
        json.dump(data, f, indent=2)
    return fichier_archive

def main():
    print("=== DÉPARTEMENT VENTES AUTONOME ===\n")
    emails = get_emails()
    if not emails:
        print("⚠️ Aucun email à vendre. Lancez d'abord l'agence Kays.")
        return
    
    nb = len(emails)
    print(f"📧 {nb} emails disponibles à la vente.")
    
    # Demander le montant
    try:
        montant = float(input("💰 Montant en euros (ex: 49.99) : "))
    except ValueError:
        print("Montant invalide.")
        return
    
    description = f"{OBJET} - {nb} emails"
    lien = generer_lien_paypal(montant, description)
    
    print("\n🔗 LIEN DE PAIEMENT À ENVOYER AU CLIENT :")
    print(lien)
    print("\n📌 Après réception du paiement, le script pourra archiver automatiquement ces emails.")
    
    reponse = input("\n➡️  Le client a-t-il payé ? (o/n) : ").lower()
    if reponse == 'o':
        archive = archiver_emails(emails)
        print(f"✅ Vente enregistrée. Emails archivés dans : {archive}")
        print("📧 Vous pouvez maintenant livrer les emails au client (fichier archive).")
    else:
        print("⏸️  Vente annulée ou en attente. Aucun email n'a été retiré.")

if __name__ == "__main__":
    main()
