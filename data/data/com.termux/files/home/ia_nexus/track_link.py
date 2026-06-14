#!/usr/bin/env python3
import sqlite3, time, os
DB = os.path.expanduser("~/ia_shared/db/nexus.db")
def track(link_id):
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO clicks (link_id, date) VALUES (?,?)", (link_id, int(time.time())))
    conn.commit()
    conn.close()
