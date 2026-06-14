import sqlite3, os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import DB_PATH
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.executescript('''
CREATE TABLE IF NOT EXISTS ventes (id INTEGER PRIMARY KEY, date TEXT, nb_emails INTEGER, montant REAL, lien TEXT, statut TEXT);
CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, date TEXT, exchange TEXT, pair TEXT, action TEXT, quantite REAL, prix REAL, pnl REAL);
CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY, email TEXT, source TEXT, score INTEGER, date_ajout TEXT, contacte INTEGER);
CREATE TABLE IF NOT EXISTS predictions (id INTEGER PRIMARY KEY, date TEXT, pair TEXT, prix_predicted REAL, confidence REAL);
CREATE TABLE IF NOT EXISTS arbitrage (id INTEGER PRIMARY KEY, date TEXT, pair TEXT, buy_exchange TEXT, sell_exchange TEXT, profit_percent REAL, executed INTEGER);
CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, date TEXT, niveau TEXT, module TEXT, message TEXT);
CREATE TABLE IF NOT EXISTS stats (cle TEXT PRIMARY KEY, valeur TEXT);
''')
conn.commit()
conn.close()
print("✅ Base SQLite initialisée")
