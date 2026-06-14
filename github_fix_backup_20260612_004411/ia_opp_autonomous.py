#!/usr/bin/env python3
import os, time, json, threading, requests, feedparser
from datetime import datetime
from web3 import Web3

PRIVATE_KEY = "5a72dc7a6a3a2d56b6e1fbdb5f4e11393190da2303df376a78277a3de2197b80"
w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.binance.org"))
account = w3.eth.account.from_key(PRIVATE_KEY)
WALLET = account.address

MEM_FILE = "ia_opp_mem.json"
LOG_FILE = "ia_opp.log"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[OPP {ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_memory():
    if os.path.exists(MEM_FILE):
        try:
            with open(MEM_FILE) as f:
                return json.load(f)
        except: pass
    return {"stats": {"cycle": 0}, "opportunities": [], "affiliate_offers": []}

def save_memory(data):
    with open(MEM_FILE, "w") as f:
        json.dump(data, f, indent=2)

class VeilleAgent(threading.Thread):
    def run(self):
        while True:
            try:
                feeds = ["https://cointelegraph.com/rss", "https://www.reddit.com/r/cryptocurrency/.rss"]
                for url in feeds:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:5]:
                        mem = load_memory()
                        mem.setdefault("opportunities", []).append({"title": entry.title, "link": entry.link, "time": str(datetime.now())})
                        if len(mem["opportunities"]) > 500:
                            mem["opportunities"] = mem["opportunities"][-200:]
                        save_memory(mem)
                        log(f"[Veille] {entry.title[:80]}")
            except Exception as e:
                log(f"[Veille] Erreur: {e}")
            time.sleep(3600)

class AffiliateAgent(threading.Thread):
    def run(self):
        while True:
            offers = [
                {"name": "Binance Earn", "link": "https://www.binance.com/en/earn", "commission": "jusqu'à 10%"},
                {"name": "AliExpress Flash Sale", "link": "https://www.aliexpress.com", "commission": "jusqu'à 8%"},
                {"name": "LBK Pro", "link": "https://www.lbkpro.net", "commission": "5%"},
            ]
            for off in offers:
                mem = load_memory()
                mem.setdefault("affiliate_offers", []).append(off)
                save_memory(mem)
                log(f"[Affiliation] Offre détectée : {off['name']}")
            time.sleep(7200)

class BalanceAgent(threading.Thread):
    def run(self):
        last_balance = 0.0
        while True:
            try:
                bal = w3.from_wei(w3.eth.get_balance(WALLET), 'ether')
                if bal > last_balance + 0.0001:
                    log(f"🎉 Don reçu ! +{bal - last_balance:.6f} BNB")
                last_balance = bal
            except: pass
            time.sleep(60)

VeilleAgent().start()
AffiliateAgent().start()
BalanceAgent().start()
log("🚀 Département Opportunité & Objectivité (100% autonome) démarré")
while True:
    mem = load_memory()
    mem["stats"]["cycle"] = mem["stats"].get("cycle", 0) + 1
    save_memory(mem)
    time.sleep(60)
