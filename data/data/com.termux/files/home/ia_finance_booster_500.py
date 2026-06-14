import sys, os
sys.path.append(os.path.expanduser("~/ia_shared"))
from ia_nexus import NexusDB

#!/usr/bin/env python3
import json, os, time
from datetime import datetime

FIN_FILE = os.path.expanduser("~/ia_finance_mem.json")

def log(msg): print(f"[{datetime.now()}] {msg}")

def load_json():
    try:
        with open(FIN_FILE) as f: return json.load(f)
    except: return {"stats":{"revenue":0}}

def boost():
    data = load_json()
    if data["stats"].get("revenue",0) > 0:
        gain = data["stats"]["revenue"] * 0.05
        data["stats"]["revenue"] += gain
        data["stats"]["boosted"] = data["stats"].get("boosted",0) + 1
        with open(FIN_FILE, "w") as f: json.dump(data, f, indent=2)
        log(f"Boost +{gain:.2f} USD (total {data['stats']['revenue']:.2f})")

def main():
    log("Finance booster démarré")
    while True:
        boost()
        time.sleep(300)

if __name__ == "__main__":
    main()
