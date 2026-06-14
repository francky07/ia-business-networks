#!/usr/bin/env python3
import sys, os, sqlite3, subprocess, time
sys.path.append(os.path.expanduser("~/ia_shared"))
from ia_nexus import NexusDB
DB = os.path.expanduser("~/ia_shared/db/nexus.db")
def get_unsold():
    conn = sqlite3.connect(DB); c=conn.cursor(); c.execute("SELECT COUNT(*) FROM emails WHERE vendu=0"); nb=c.fetchone()[0]; conn.close(); return nb
while True:
    nb = get_unsold()
    if nb >= 5:
        print(f"🧠 Vente déclenchée pour {nb} emails")
        subprocess.run(["python", os.path.expanduser("~/departement_ventes/sell_emails_paypal.py")])
    else:
        print(f"⏳ Attente: {nb} emails")
    time.sleep(60)
