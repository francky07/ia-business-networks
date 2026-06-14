#!/usr/bin/env python3
import sys, os, time, random, sqlite3
sys.path.append(os.path.expanduser("~/ia_shared"))
from ia_nexus import NexusDB, EventBus

while True:
    # Vérifier emails
    rows = NexusDB.execute("SELECT COUNT(*) FROM emails WHERE vendu=0", fetch=True)
    nb_emails = rows[0][0] if rows else 0
    if nb_emails >= 5:
        print(f"🧠 Décision: vendre {nb_emails} emails")
        EventBus.emit("vente", {"nb": nb_emails})
    time.sleep(30)
