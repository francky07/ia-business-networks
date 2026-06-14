#!/usr/bin/env python3
import schedule, time, subprocess, sqlite3, os
DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")

def adaptative_schedule():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT AVG(montant) FROM ventes WHERE date > strftime('%s','now','-1 day')")
    avg = c.fetchone()[0] or 0
    conn.close()
    if avg > 0.1:
        # Ventes élevées : augmenter la fréquence des actions
        print("📈 Activité élevée – réduction des cycles")
    else:
        print("📉 Activité faible – réduction des ressources")

schedule.every(1).hour.do(adaptative_schedule)
while True:
    schedule.run_pending()
    time.sleep(60)
