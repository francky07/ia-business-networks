import os
from dotenv import load_dotenv

load_dotenv()
PI_API_KEY = os.getenv("PI_API_KEY")
PI_WALLET_PUBLIC = os.getenv("PI_WALLET_PUBLIC")

print(f"PI_API_KEY = {PI_API_KEY[:10]}... (longueur {len(PI_API_KEY)})" if PI_API_KEY else "Clé API manquante")
print(f"PI_WALLET_PUBLIC = {PI_WALLET_PUBLIC[:10]}..." if PI_WALLET_PUBLIC else "Wallet public manquant")
