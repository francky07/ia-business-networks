#!/usr/bin/env python3
"""
Module d'auto‑correction pour le CEO – surveille les erreurs et applique des correctifs.
Ne modifie pas la logique du CEO.
"""
import os
import time
import subprocess
import re
import glob

LOG_FILE = os.path.expanduser("~/ceo_supreme.log")
CEO_SCRIPT = os.path.expanduser("~/ia_nexus/ceo_supreme.py")
ENV_FILE = os.path.expanduser("~/.env_ia_business")

def log(msg):
    print(f"[AutoCorrect] {msg}")

def check_and_fix():
    if not os.path.exists(LOG_FILE):
        return
    with open(LOG_FILE, "r") as f:
        content = f.read()
    # 1. Vérifier si le CEO est mort (plus de logs récents)
    if "CEO Suprême démarré" not in content:
        log("Le CEO ne semble pas démarré → tentative de relance")
        subprocess.run(["pkill", "-f", "ceo_supreme.py"])
        subprocess.Popen(["nohup", "python", CEO_SCRIPT, ">", "~/ceo_supreme.log", "2>&1", "&"], shell=True)
        return

    # 2. Erreur PayPal (token invalide)
    if "Erreur PayPal" in content or "Échec token PayPal" in content:
        log("Erreur PayPal détectée → tentative de nettoyage du cache")
        # On peut simplement relancer le CEO pour qu'il réinitialise le token
        subprocess.run(["pkill", "-f", "ceo_supreme.py"])
        subprocess.Popen(["nohup", "python", CEO_SCRIPT, ">", "~/ceo_supreme.log", "2>&1", "&"], shell=True)
        return

    # 3. Erreur BNB (connexion Web3)
    if "Erreur BNB" in content:
        log("Erreur BNB détectée → redémarrage dans 10s")
        time.sleep(10)
        subprocess.run(["pkill", "-f", "ceo_supreme.py"])
        subprocess.Popen(["nohup", "python", CEO_SCRIPT, ">", "~/ceo_supreme.log", "2>&1", "&"], shell=True)
        return

    # 4. Vérifier que les clés API sont présentes
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            env_content = f.read()
        if "PAYPAL_API_CLIENT_ID" not in env_content or "PAYPAL_API_CLIENT_SECRET" not in env_content:
            log("Clés PayPal manquantes → ajout automatique (fichier .env_ia_business)")
            # Ajouter des clés de test (à remplacer par vos vraies clés)
            with open(ENV_FILE, "a") as f:
                f.write("\nexport PAYPAL_API_CLIENT_ID='AWtfyaIH1TG63ijQjFO40fapigxovoqoUz2_8iWU1-8qSlEarr2cvkp8iMBYZJnlcx5SYirhr1Tj47Uv'\n")
                f.write("export PAYPAL_API_CLIENT_SECRET='EKIwuxjzkqWkdLfmmiYt3lVSs_HEuEH_8H-14kBSj1OM-Fb9I82VsgPYymmwHOaVcD6jkdMg5-Jv-JKh'\n")
                f.write("export PAYPAL_API_MODE='sandbox'\n")
            subprocess.run(["pkill", "-f", "ceo_supreme.py"])
            subprocess.Popen(["nohup", "python", CEO_SCRIPT, ">", "~/ceo_supreme.log", "2>&1", "&"], shell=True)
            return

    # 5. Nettoyage des logs trop volumineux
    if os.path.getsize(LOG_FILE) > 10 * 1024 * 1024:  # 10 Mo
        log("Fichier log trop volumineux → rotation")
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()[-1000:]  # garde les 1000 dernières lignes
        with open(LOG_FILE, "w") as f:
            f.writelines(lines)

def main():
    log("Module d'auto‑correction démarré")
    while True:
        check_and_fix()
        time.sleep(60)  # toutes les minutes

if __name__ == "__main__":
    main()
