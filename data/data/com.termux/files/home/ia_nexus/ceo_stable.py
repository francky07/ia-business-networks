#!/usr/bin/env python3
import time, sqlite3, subprocess, os
DB = os.path.expanduser("~/ia_shared/db/nexus.db")
while True:
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM emails WHERE vendu=0")
    stock = c.fetchone()[0]
    conn.close()
    if stock > 100:
        print(f"🧠 CEO: stock élevé ({stock}) → déclenchement vente")
        subprocess.run(["python", os.path.expanduser("~/departement_ventes/sell_emails_paypal.py")])
    else:
        print(f"✅ Stock normal ({stock})")
    time.sleep(600)
