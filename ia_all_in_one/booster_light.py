import asyncio
import json
from config import WALLET_FILE

async def booster_light():
    print("🚀 Boosters asynchrones démarrés (1000 tâches légères)")
    tasks = []
    for i in range(1000):
        tasks.append(asyncio.create_task(single_booster(i)))
    await asyncio.gather(*tasks)

async def single_booster(booster_id):
    while True:
        await asyncio.sleep(60)
        try:
            with open(WALLET_FILE, 'r') as f:
                data = json.load(f)
                # Afficher une fois toutes les minutes si vous voulez
                # print(f"[Booster {booster_id}] BNB: {data.get('bnb_balance',0):.6f}")
        except:
            pass
