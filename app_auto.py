#!/usr/bin/env python3
"""
Application autonome – génère et vend du contenu (articles, vidéos, etc.)
Lit les clés depuis ~/.env_ia_business
"""
import os, sys, time, json, random, requests
from datetime import datetime

sys.path.append(os.path.expanduser("~/ia_shared"))
try:
    from ia_nexus import ConfigManager
except ImportError:
    ConfigManager = type('ConfigManager', (), {'get': lambda self, k, d=None: os.getenv(k, d)})()

OPENAI_API_KEY = ConfigManager.get("OPENAI_API_KEY")
PAYPAL_EMAIL = ConfigManager.get("PAYPAL_EMAIL", "faraseck@hotmail.fr")

def log(msg): print(f"[APP AUTO {datetime.now()}] {msg}")

def generate_article(topic="crypto"):
    if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-"):
        try:
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
            data = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": f"Rédige un article court sur {topic}"}]}
            r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=15)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            log(f"OpenAI erreur: {e}")
    return f"Article générique sur {topic}."

def publish_article(article):
    # Ici, publier sur un site web (via GitHub Pages, ou autre)
    with open("auto_article.html", "w") as f:
        f.write(f"<html><body><h1>Article auto</h1><p>{article}</p><p>Paiement: <a href='https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&amount=0.99&currency_code=USD'>Acheter 0.99 USD</a></p></body></html>")
    log("Article publié localement (auto_article.html)")

def main():
    log("Application auto démarrée")
    while True:
        topic = random.choice(["crypto", "IA", "investissement", "trading"])
        article = generate_article(topic)
        publish_article(article)
        time.sleep(3600)  # toutes les heures

if __name__ == "__main__":
    main()
