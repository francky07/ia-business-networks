#!/usr/bin/env python3
import json, os, requests, base64
from datetime import datetime

# Charger les clés PayPal
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/.env_ia_business"))

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")

def get_paypal_token():
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    if PAYPAL_MODE == "live":
        url = "https://api-m.paypal.com/v1/oauth2/token"
    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}
    resp = requests.post(url, headers=headers, data=data)
    if resp.status_code != 200:
        print(f"❌ Erreur token: {resp.status_code} - {resp.text}")
        return None
    return resp.json().get("access_token")

def create_paypal_order(amount=5.00):
    token = get_paypal_token()
    if not token:
        return None
    url = "https://api-m.sandbox.paypal.com/v2/checkout/orders"
    if PAYPAL_MODE == "live":
        url = "https://api-m.paypal.com/v2/checkout/orders"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{"amount": {"currency_code": "USD", "value": str(amount)}}],
        "application_context": {
            "return_url": "https://example.com/return",
            "cancel_url": "https://example.com/cancel"
        }
    }
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 201:
        print(f"❌ Erreur création commande: {resp.status_code} - {resp.text}")
        return None
    data = resp.json()
    # Chercher le lien "approve"
    for link in data.get("links", []):
        if link.get("rel") == "approve":
            return link.get("href")
    print("❌ Aucun lien 'approve' trouvé dans la réponse")
    print("Réponse complète:", json.dumps(data, indent=2))
    return None

def get_emails():
    keys_file = os.path.expanduser("~/agence_kays/keys.json")
    if not os.path.exists(keys_file):
        return []
    with open(keys_file) as f:
        data = json.load(f)
    return data.get("emails", [])

def main():
    emails = get_emails()
    if not emails:
        print("❌ Aucun email disponible dans agence_kays")
        return
    print(f"📧 {len(emails)} emails prêts à être vendus")
    # Vendre le lot pour 5 USD
    pay_link = create_paypal_order(5.00)
    if pay_link:
        print(f"💰 LIEN DE PAIEMENT : {pay_link}")
        # Ici vous pouvez vider ou marquer les emails comme vendus
        # Par exemple, sauvegarder une copie et vider la liste
        backup_file = os.path.expanduser(f"~/agence_kays/emails_sold_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(backup_file, "w") as f:
            json.dump({"emails": emails, "paypal_link": pay_link}, f)
        # Vider la liste après vente (optionnel)
        # with open(os.path.expanduser("~/agence_kays/keys.json"), "w") as f:
        #     json.dump({"emails": [], "github_tokens": []}, f)
        # print("✅ Liste des emails vidée après vente")
    else:
        print("❌ Échec de création du lien PayPal")

if __name__ == "__main__":
    main()
