#!/usr/bin/env python3
import os, time, json, random, threading, requests
from datetime import datetime

MEM_FILE = "ia_opp_mem.json"
LOG_FILE = "ia_opp.log"
HUB_URL = "http://localhost:5003"
BOT_ID = "opp_agents"

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
    return {"stats": {"cycle":0, "actions":0}, "opportunities":[], "products":[], "campaigns":[]}

def save_memory(data):
    with open(MEM_FILE, "w") as f:
        json.dump(data, f, indent=2)

def hub_ping():
    try:
        requests.post(f"{HUB_URL}/api/register", json={"bot_id": BOT_ID, "info": {"type": "opportunity", "agents": 500}}, timeout=2)
        while True:
            mem = load_memory()
            state = {"cycle": mem["stats"].get("cycle",0), "opportunities": len(mem.get("opportunities",[]))}
            requests.post(f"{HUB_URL}/api/ping", json={"bot_id": BOT_ID, "state": state}, timeout=2)
            time.sleep(30)
    except: pass

threading.Thread(target=hub_ping, daemon=True).start()

class VeilleAgent(threading.Thread):
    def __init__(self, name):
        super().__init__(daemon=True)
        self.name = name
    def run(self):
        while True:
            trends = ["IA générative", "Web3", "automatisation marketing", "dropshipping", "SaaS no-code"]
            selected = random.choice(trends)
            mem = load_memory()
            mem.setdefault("opportunities", []).append({"type": "trend", "value": selected, "time": str(datetime.now())})
            if len(mem["opportunities"]) > 1000:
                mem["opportunities"] = mem["opportunities"][-500:]
            save_memory(mem)
            log(f"[Veille] Tendance détectée : {selected}")
            time.sleep(random.randint(600, 1800))

for i in range(100):
    VeilleAgent(f"Veille_{i}").start()

class ProductAgent(threading.Thread):
    def __init__(self, name):
        super().__init__(daemon=True)
        self.name = name
    def run(self):
        while True:
            product_types = ["cours en ligne", "ebook", "template Shopify", "plugin WordPress", "bot Telegram"]
            ptype = random.choice(product_types)
            product = {
                "name": f"{ptype.capitalize()} IA {random.randint(1,999)}",
                "type": ptype,
                "price": round(random.uniform(9.99, 199.99), 2),
                "created_at": str(datetime.now())
            }
            mem = load_memory()
            mem.setdefault("products", []).append(product)
            if len(mem["products"]) > 200:
                mem["products"] = mem["products"][-100:]
            save_memory(mem)
            log(f"[Product] Nouveau produit proposé : {product['name']} ({product['price']}€)")
            time.sleep(random.randint(1800, 3600))

for i in range(100):
    ProductAgent(f"Product_{i}").start()

class MarketingAgent(threading.Thread):
    def __init__(self, name):
        super().__init__(daemon=True)
        self.name = name
    def run(self):
        while True:
            campaigns = ["Facebook Ads", "Google Ads", "Email sequence", "SEO article"]
            camp = random.choice(campaigns)
            mem = load_memory()
            mem.setdefault("campaigns", []).append({"type": camp, "status": "proposed", "budget": round(random.uniform(50, 500), 2), "time": str(datetime.now())})
            save_memory(mem)
            log(f"[Marketing] Campagne proposée : {camp}")
            time.sleep(random.randint(900, 2700))

for i in range(100):
    MarketingAgent(f"Marketing_{i}").start()

class SupportAgent(threading.Thread):
    def __init__(self, name):
        super().__init__(daemon=True)
        self.name = name
    def run(self):
        while True:
            faqs = ["Délai de livraison", "Paiement sécurisé", "Retour produit", "Abonnement mensuel"]
            q = random.choice(faqs)
            log(f"[Support] Réponse automatique à la FAQ '{q}'")
            time.sleep(random.randint(300, 900))

for i in range(100):
    SupportAgent(f"Support_{i}").start()

class ComptaAgent(threading.Thread):
    def __init__(self, name):
        super().__init__(daemon=True)
        self.name = name
    def run(self):
        while True:
            mem = load_memory()
            revenue = round(random.uniform(10, 500), 2)
            mem["stats"]["revenue_total"] = mem["stats"].get("revenue_total", 0) + revenue
            mem["stats"]["last_transaction"] = {"amount": revenue, "time": str(datetime.now())}
            save_memory(mem)
            log(f"[Compta] Transaction simulée : +{revenue}€")
            time.sleep(random.randint(600, 1800))

for i in range(100):
    ComptaAgent(f"Compta_{i}").start()

log("✅ 500 agents actifs du département Opportunité & Objectivité démarrés")
while True:
    mem = load_memory()
    mem["stats"]["cycle"] = mem["stats"].get("cycle", 0) + 1
    mem["stats"]["actions"] = mem["stats"].get("actions", 0) + 1
    save_memory(mem)
    time.sleep(60)
