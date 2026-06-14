import json
import time
from config import WALLET_FILE

# On évite web3 pour éviter les erreurs d'installation sur Termux
# Si vous installez web3, vous pourrez décommenter plus tard.

def get_bnb_balance():
    wallet = load_wallet()
    return wallet.get('bnb_balance', 0.0)

def save_wallet(bnb_balance, earnings_usd):
    data = {
        'bnb_balance': float(bnb_balance),
        'total_earnings_usd': float(earnings_usd),
        'last_update': time.time()
    }
    with open(WALLET_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_wallet():
    try:
        with open(WALLET_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'bnb_balance': 0.0, 'total_earnings_usd': 0.0}
