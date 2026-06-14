import asyncio
import random
from config import NB_AFFILIATION, NB_MICROTASK, NB_CONTENU, NB_ARBITRAGE, NB_STAKING, NB_API_CREATOR, NB_ACCOUNT_CREATOR, CYCLE_SECONDS
from agent_async import AsyncAgent
from booster_light import booster_light
from wallet_manager import get_bnb_balance, save_wallet
from dashboard import dashboard

async def main():
    report_queue = asyncio.Queue()
    agents_queues = {}
    agents = []
    agent_id = 0

    def create_agent(agent_type, count):
        nonlocal agent_id
        for _ in range(count):
            q = asyncio.Queue()
            agents_queues[agent_id] = q
            agent = AsyncAgent(agent_id, agent_type, q, report_queue)
            agents.append(agent)
            agent_id += 1

    create_agent('affiliation', NB_AFFILIATION)
    create_agent('microtask', NB_MICROTASK)
    create_agent('contenu', NB_CONTENU)
    create_agent('arbitrage', NB_ARBITRAGE)
    create_agent('staking', NB_STAKING)
    create_agent('api_creator', NB_API_CREATOR)
    create_agent('account_creator', NB_ACCOUNT_CREATOR)

    print(f"✅ {len(agents)} agents asynchrones créés")

    # Lancement des agents
    agent_tasks = [asyncio.create_task(agent.run()) for agent in agents]

    # Lancement de la directrice (simplifiée)
    async def director_loop():
        cycle = 0
        total_earnings = 0.0
        while True:
            cycle += 1
            # Collecte des rapports
            reports = []
            while not report_queue.empty():
                try:
                    reports.append(report_queue.get_nowait())
                except asyncio.QueueEmpty:
                    break
            for r in reports:
                total_earnings += r.get('gain', 0.0)

            # Allocation simplifiée : on alterne les actions
            actions = ['post_tweet', 'solve_captcha', 'write_article', 'scan_free_offers', 'stake_bnb']
            for i, q in enumerate(agents_queues.values()):
                action = actions[i % len(actions)]
                await q.put({'action': action, 'params': {}})

            if cycle % 60 == 0 and total_earnings > 0:
                print(f"💱 Conversion de {total_earnings:.2f} USD en BNB (simulée)")
                bnb = get_bnb_balance() + (total_earnings / 520)
                save_wallet(bnb, total_earnings)
                total_earnings = 0.0

            await asyncio.sleep(CYCLE_SECONDS)

    # Lancement de la directrice et du dashboard
    asyncio.create_task(director_loop())
    asyncio.create_task(dashboard())
    asyncio.create_task(booster_light())

    # Attente infinie
    await asyncio.gather(*agent_tasks)

if __name__ == "__main__":
    asyncio.run(main())

# Ajout d'un affichage dans la boucle director_loop
# (On va plutôt remplacer le fichier par une version corrigée)
