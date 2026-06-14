import asyncio
import json
from config import WALLET_FILE, NB_BOOSTERS_TOTAL

async def booster_light():
    print(f"🚀 {NB_BOOSTERS_TOTAL} boosters démarrés")
    tasks = [asyncio.create_task(single_booster(i)) for i in range(NB_BOOSTERS_TOTAL)]
    await asyncio.gather(*tasks)

async def single_booster(booster_id):
    while True:
        await asyncio.sleep(60)
        try:
            with open(WALLET_FILE, 'r') as f:
                data = json.load(f)
        except:
            pass
