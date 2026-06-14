import asyncio
import random
from config import NB_AFFILIATION, NB_MICROTASK, NB_CONTENU, NB_ARBITRAGE, NB_STAKING, NB_API_CREATOR, NB_ACCOUNT_CREATOR, CYCLE_SECONDS
from agent_async import AsyncAgent
from booster_light import booster_light
from wallet_manager import get_bnb_balance, save_wallet, load_wallet
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

    # Démarrer les agents
    agent_tasks = [asyncio.create_task(agent.run()) for agent in agents]

    # Laisser le temps aux agents de démarrer
    await asyncio.sleep(2)

    # Directrice
    async def director_loop():
        cycle = 0
        total_earnings = 0.0
        actions = ['post_tweet', 'solve_captcha', 'write_article', 'scan_free_offers', 'stake_bnb']
        while True:
            cycle += 1
            print(f"\n[Cycle {cycle}] Envoi des commandes...")
            # Envoyer les commandes à TOUS les agents
            for agent_id, q in agents_queues.items():
                action = actions[agent_id % len(actions)]
                await q.put({'action': action, 'params': {}})
            # Attendre un peu que les agents exécutent
            await asyncio.sleep(2)
            # Récupérer les rapports
            reports = []
            while not report_queue.empty():
                try:
                    r = report_queue.get_nowait()
                    reports.append(r)
                except asyncio.QueueEmpty:
                    break
            for r in reports:
                gain = r.get('gain', 0.0)
                total_earnings += gain
                print(f"[Directrice] Agent {r['agent_id']} a gagné {gain:.6f} USD")
            print(f"[Cycle {cycle}] Gains cumulés (non convertis) : {total_earnings:.4f} USD")
            # Conversion toutes les heures (60 cycles)
            if cycle % 60 == 0 and total_earnings > 0:
                print(f"💱 Conversion de {total_earnings:.2f} USD en BNB")
                bnb_balance = get_bnb_balance()
                new_bnb = bnb_balance + (total_earnings / 520.0)
                save_wallet(new_bnb, total_earnings)
                total_earnings = 0.0
            await asyncio.sleep(CYCLE_SECONDS)

    # Lancer la directrice, le dashboard et les boosters
    asyncio.create_task(director_loop())
    asyncio.create_task(dashboard())
    asyncio.create_task(booster_light())

    # Attendre que les agents tournent
    await asyncio.gather(*agent_tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé")
