import json
import time
from config import WALLET_FILE

def get_bnb_balance():
    try:
        with open(WALLET_FILE, 'r') as f:
            data = json.load(f)
            return data.get('bnb_balance', 0.0)
    except:
        return 0.0

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
