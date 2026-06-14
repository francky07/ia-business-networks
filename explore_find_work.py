#!/usr/bin/env python3
import os
import re
import json
from datetime import datetime

# Dossiers à explorer (ajustez selon votre système)
DOSSIERS_A_EXPLORER = [
    os.path.expanduser("~"),                 # votre home
    os.path.expanduser("~/agence_kays"),
    os.path.expanduser("~/departement_ventes"),
    os.path.expanduser("~/ia_mainnet_reelle"),
    os.path.expanduser("~/oeil_de_dieu"),
    os.path.expanduser("~/trading_bot"),
]

# Extensions de fichiers à analyser
EXTENSIONS = [".py", ".sh", ".json", ".env", ".txt", ".log", ".yml", ".yaml", ".toml"]

# Motifs de recherche (emails, clés API, etc.)
PATTERNS = {
    "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    "github_token": r'ghp_[a-zA-Z0-9]{36}',
    "paypal_client_id": r'[A-Za-z0-9_-]{40,}',
    "paypal_secret": r'[A-Za-z0-9_-]{40,}',
    "stripe_key": r'sk_(test|live)_[a-zA-Z0-9]+',
    "openai_key": r'sk-[a-zA-Z0-9]{48,}',
    "wallet_private_key": r'0x[a-fA-F0-9]{64}',
    "api_key": r'[A-Za-z0-9]{32,}',
    "bearer_token": r'[A-Za-z0-9\-_]{20,}\.[A-Za-z0-9\-_]{20,}\.[A-Za-z0-9\-_]{20,}',
}

def search_in_file(filepath):
    """Recherche les motifs dans un fichier et retourne les correspondances."""
    results = {}
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            for name, pattern in PATTERNS.items():
                matches = re.findall(pattern, content)
                if matches:
                    results[name] = list(set(matches))  # uniques
    except Exception as e:
        pass
    return results

def main():
    rapport = {
        "date": datetime.now().isoformat(),
        "machine": os.uname().nodename if hasattr(os, 'uname') else "unknown",
        "fichiers_analyses": [],
        "decouvertes": {}
    }

    for dossier in DOSSIERS_A_EXPLORER:
        if not os.path.isdir(dossier):
            continue
        for root, dirs, files in os.walk(dossier):
            # Ignorer certains dossiers (ex: .git, __pycache__)
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in EXTENSIONS:
                    filepath = os.path.join(root, file)
                    rapport["fichiers_analyses"].append(filepath)
                    dec = search_in_file(filepath)
                    if dec:
                        rapport["decouvertes"][filepath] = dec

    # Sauvegarde du rapport
    rapport_file = os.path.expanduser("~/rapport_exploration.json")
    with open(rapport_file, "w") as f:
        json.dump(rapport, f, indent=2)

    # Affichage synthétique
    print(f"🔍 Exploration terminée. Rapport sauvegardé dans {rapport_file}")
    print(f"📁 Fichiers analysés : {len(rapport['fichiers_analyses'])}")
    print(f"💡 Découvertes : {len(rapport['decouvertes'])} fichiers avec informations sensibles")

    # Optionnel : afficher les découvertes
    for fpath, dec in rapport["decouvertes"].items():
        print(f"\n📄 {fpath}")
        for dtype, valeurs in dec.items():
            print(f"   {dtype} : {', '.join(valeurs[:3])}{'...' if len(valeurs)>3 else ''}")

if __name__ == "__main__":
    main()
