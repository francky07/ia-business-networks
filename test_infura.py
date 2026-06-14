import os, requests, json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/ia_web/.env"))
key = os.getenv("INFURA_KEY")
if not key:
    print("❌ Clé Infura non trouvée dans .env")
    exit(1)

url = f"https://mainnet.infura.io/v3/{key}"
print(f"🔍 Test avec curl-like via requests...")
try:
    r = requests.post(url, json={"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}, timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("✅ Infura OK")
        data = r.json()
        print(f"Dernier bloc: {int(data['result'],16)}")
    else:
        print(f"❌ Erreur HTTP {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"❌ Exception: {e}")
