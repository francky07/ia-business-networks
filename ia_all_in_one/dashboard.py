import asyncio
import os
import time
from wallet_manager import get_bnb_balance, load_wallet
from config import NB_AGENTS_TOTAL, NB_BOOSTERS_TOTAL

async def dashboard():
    while True:
        os.system('clear')
        bnb = get_bnb_balance()
        wallet = load_wallet()
        print("="*70)
        print("   🌟 IA BUSINESS ALL-IN-ONE – 2000 agents + 1000 boosters")
        print("="*70)
        print(f"💰 BNB wallet : {bnb:.6f} BNB")
        print(f"💰 Gains totaux (USD) : {wallet.get('total_earnings_usd', 0):.2f} USD")
        print(f"👥 Agents : {NB_AGENTS_TOTAL} | Boosters : {NB_BOOSTERS_TOTAL}")
        print(f"🔄 Cycle : 60 secondes")
        print(f"📡 Prochain rafraîchissement dans ~ {60 - (time.time() % 60):.1f} s")
        print("="*70)
        await asyncio.sleep(5)
