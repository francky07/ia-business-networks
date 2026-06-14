#!/usr/bin/env python3
import sys, os, urllib.parse, sqlite3, time
sys.path.append(os.path.expanduser("~/ia_shared"))
from ia_nexus import NexusDB
PAYPAL_EMAIL = "faraseck@hotmail.fr"
def generer_lien(montant, desc):
    params = {"cmd":"_xclick","business":PAYPAL_EMAIL,"amount":f"{montant:.2f}","currency_code":"USD","item_name":desc,"no_shipping":"1"}
    return "https://www.paypal.com/cgi-bin/webscr?" + urllib.parse.urlencode(params)
def main():
    emails = NexusDB.get_unsold_emails(limit=500)
    if not emails: return
    ids = [e["id"] for e in emails]
    nb = len(ids)
    montant = nb * 0.005
    lien = generer_lien(montant, f"{nb} emails")
    print(f"💰 LIEN DE PAIEMENT : {lien}")
    NexusDB.mark_emails_sold(ids)
    NexusDB.add_vente(nb, montant, lien)
    print(f"✅ {nb} emails vendus")
if __name__ == "__main__":
    import asyncio; asyncio.run(main())
