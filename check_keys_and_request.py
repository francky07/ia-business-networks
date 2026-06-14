#!/usr/bin/env python3
import os, json, time
from dotenv import load_dotenv

ENV_FILE = os.path.expanduser("~/.env_finance")
REQUEST_FILE = os.path.expanduser("~/key_requests.json")

# Liste des clés critiques (celles qui doivent absolument être réelles)
REQUIRED_KEYS = [
    "BINANCE_API_KEY",
    "BINANCE_API_SECRET",
    "STRIPE_SECRET_KEY",
    "CLICKWORKER_API_KEY",
    "OPENAI_API_KEY"
]

def load_env():
    load_dotenv(ENV_FILE)
    return {k: os.getenv(k) for k in REQUIRED_KEYS}

def load_requests():
    try:
        with open(REQUEST_FILE) as f:
            return json.load(f)
    except:
        return {"pending": [], "fulfilled": []}

def save_requests(data):
    with open(REQUEST_FILE, "w") as f:
        json.dump(data, f, indent=2)

def main():
    while True:
        env = load_env()
        missing = [k for k, v in env.items() if not v]
        if missing:
            req = load_requests()
            for key in missing:
                if key not in req["pending"] and key not in req["fulfilled"]:
                    req["pending"].append(key)
                    print(f"📢 Demande de clé manquante : {key}")
            save_requests(req)
        time.sleep(60)  # vérifie toutes les minutes

if __name__ == "__main__":
    main()
