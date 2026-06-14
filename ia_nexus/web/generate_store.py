#!/usr/bin/env python3
import sqlite3
import os
import time
import json
import subprocess
from datetime import datetime

DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
AFFILIATE_FILE = os.path.expanduser("~/ia_shared/affiliates/links.html")
REPO_PATH = os.path.expanduser("~/ia-net-blog-pro")
OUTPUT_FILE = os.path.join(REPO_PATH, "index.html")
PAYPAL_EMAIL = "faraseck@hotmail.fr"
BNB_ADDRESS = "0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363"
BTC_ADDRESS = "bc1q..."; USDT_ADDRESS = "0x..."

def get_bnb_balance():
    try:
        with open(os.path.expanduser("~/ia_mem_pro.json")) as f:
            data = json.load(f)
            return data.get("last_balance", 0)
    except:
        return 0

def get_affiliate_links():
    try:
        with open(AFFILIATE_FILE) as f:
            return f.read()
    except:
        return "<ul><li>Liens d'affiliation à configurer</li></ul>"

def get_emails():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT email FROM emails WHERE vendu=0 ORDER BY date_creation LIMIT 100")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_comptes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT type, identifiant, mot_de_passe, prix FROM comptes WHERE vendu=0 ORDER BY date_creation LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return rows

def generate_html(emails, comptes, bnb_balance, affiliate_links):
    nb_emails = len(emails)
    montant_emails = nb_emails * 0.01
    paypal_link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&amount={montant_emails:.2f}&currency_code=USD&item_name={nb_emails}+emails&no_shipping=1"
    
    email_list = "".join([f"<li>{e}</li>" for e in emails]) if emails else "<li>Aucun email disponible</li>"
    
    comptes_html = ""
    for typ, ident, pwd, prix in comptes:
        comptes_html += f"<li><strong>{typ}</strong> : {ident} | mot de passe : {pwd} | prix : {prix} USD</li>"
    if not comptes_html:
        comptes_html = "<li>Aucun compte disponible</li>"
    
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>IA Business – Boutique</title>
<style>
body {{ font-family: Arial; margin: 40px; background: #f5f5f5; }}
.container {{ max-width: 1000px; margin: auto; background: white; padding: 20px; border-radius: 10px; }}
.flex {{ display: flex; gap: 40px; flex-wrap: wrap; }}
.shop {{ flex: 2; }}
.affiliate {{ flex: 1; background: #f0f0f0; padding: 15px; border-radius: 8px; }}
.bnb {{ background: #e8f5e9; padding: 10px; border-radius: 5px; margin-top: 15px; text-align: center; }}
.address {{ font-family: monospace; word-break: break-all; background: #fff; padding: 8px; border-radius: 4px; }}
.btn {{ display: inline-block; background: #0070ba; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; }}
.email-list, .comptes-list {{ background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0; max-height: 300px; overflow-y: auto; }}
</style>
</head>
<body>
<div class="container">
    <h1>🤖 IA Business – Boutique automatique</h1>
    <div class="flex">
        <div class="shop">
            <h2>📧 Emails temporaires</h2>
            <p>{nb_emails} emails disponibles – Prix : {montant_emails:.2f} USD</p>
            <div class="email-list"><ul>{email_list}</ul></div>
            <a href="{paypal_link}" class="btn">Acheter les emails</a>
            <h2>👤 Comptes à vendre</h2>
            <div class="comptes-list"><ul>{comptes_html}</ul></div>
        </div>
        <div class="affiliate">
            <h2>🔗 Liens de parrainage</h2>
            {affiliate_links}
            <div class="bnb">
                💰 Staking BNB : {bnb_balance:.6f} BNB<br>
                📩 Dons : <div class="address">{BNB_ADDRESS}</div>
BTC_ADDRESS = "bc1q..."; USDT_ADDRESS = "0x..."
            </div>
        </div>
    </div>
    <div class="footer">Mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
</div>
</body>
</html>"""
    return html

def main():
    emails = get_emails()
    comptes = get_comptes()
    bnb = get_bnb_balance()
    aff = get_affiliate_links()
    html = generate_html(emails, comptes, bnb, aff)
    with open(OUTPUT_FILE, "w") as f:
        f.write(html)
    subprocess.run(["git", "-C", REPO_PATH, "add", "index.html"], check=True)
    subprocess.run(["git", "-C", REPO_PATH, "commit", "-m", "Ajout section comptes à vendre"], check=True)
    subprocess.run(["git", "-C", REPO_PATH, "push", "origin", "main"], check=True)

if __name__ == "__main__":
    main()
