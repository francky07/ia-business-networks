import sqlite3, json, os, time, threading, queue
DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
class NexusDB:
    @staticmethod
    def _conn(): return sqlite3.connect(DB_PATH, check_same_thread=False)
    @staticmethod
    def execute(q, p=(), f=False):
        with NexusDB._conn() as c:
            cur = c.cursor()
            cur.execute(q, p)
            if f: return cur.fetchall()
            c.commit()
    @staticmethod
    def add_email(email, src="agence_kays"): NexusDB.execute("INSERT INTO emails (email, source, date_creation, vendu) VALUES (?,?,?,?)", (email, src, int(time.time()), 0))
    @staticmethod
    def get_unsold_emails(limit=100): rows = NexusDB.execute("SELECT id, email FROM emails WHERE vendu=0 ORDER BY date_creation LIMIT ?", (limit,), f=True); return [{"id":r[0], "email":r[1]} for r in rows]
    @staticmethod
    def mark_emails_sold(ids): NexusDB.execute(f"UPDATE emails SET vendu=1 WHERE id IN ({','.join('?'*len(ids))})", ids)
    @staticmethod
    def add_vente(nb, montant, lien): NexusDB.execute("INSERT INTO ventes (date, nb_emails, montant, lien, statut) VALUES (?,?,?,?,?)", (int(time.time()), nb, montant, lien, "paypal"))
    @staticmethod
    def update_bot_stats(name, cycle, actions, extra=""): NexusDB.execute("REPLACE INTO stats_bots (bot_name, cycle, actions, last_update, extra) VALUES (?,?,?,?,?)", (name, cycle, actions, int(time.time()), extra))
class ConfigManager:
    @staticmethod
    def get(key, default=None):
        env_file = os.path.expanduser("~/.env_ia_business")
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    if line.startswith("export "): line = line[7:]
                    if "=" in line and line.split("=")[0].strip() == key:
                        return line.split("=",1)[1].strip().strip("\"'")
        return default
