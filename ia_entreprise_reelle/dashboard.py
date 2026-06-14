import asyncio
import os
import time
from wallet_manager import get_bnb_balance
from config import NB_AGENTS_TOTAL, NB_BOOSTERS_TOTAL

async def dashboard():
    while True:
        os.system('clear')
        bnb = get_bnb_balance()
        print("="*70)
        print("   🌟 IA BUSINESS RÉELLE – Gains réels + conversion BNB")
        print("="*70)
        print(f"💰 BNB wallet : {bnb:.6f} BNB")
        print(f"👥 Agents : {NB_AGENTS_TOTAL} | Boosters : {NB_BOOSTERS_TOTAL}")
        print("   (dont 50 agents 'api_convert')")
        print(f"🔄 Cycle : 60 secondes")
        print("="*70)
        await asyncio.sleep(5)
