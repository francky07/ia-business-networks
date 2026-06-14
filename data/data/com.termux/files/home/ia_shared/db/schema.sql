CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    source TEXT,
    date_creation INTEGER,
    vendu INTEGER DEFAULT 0,
    prix REAL
);

CREATE TABLE IF NOT EXISTS ventes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date INTEGER,
    nb_emails INTEGER,
    montant REAL,
    lien TEXT,
    statut TEXT
);

CREATE TABLE IF NOT EXISTS stats_bots (
    bot_name TEXT PRIMARY KEY,
    cycle INTEGER,
    actions INTEGER,
    last_update INTEGER,
    extra TEXT
);

CREATE TABLE IF NOT EXISTS opportunites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair TEXT,
    score INTEGER,
    date INTEGER,
    traite INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT
);
