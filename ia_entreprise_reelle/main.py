import asyncio
import json
from config import (NB_AFFILIATION, NB_MICROTASK, NB_CONTENU, NB_ARBITRAGE,
                    NB_STAKING, NB_API_CREATOR, NB_HUB_BROKERS, NB_DIRECTION,
                    NB_FINANCE, NB_API_CONVERT)
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
    create_agent('hub_broker', NB_HUB_BROKERS)
    create_agent('direction', NB_DIRECTION)
    create_agent('finance', NB_FINANCE)
    create_agent('api_convert', NB_API_CONVERT)

    print(f"✅ {len(agents)} agents créés (dont {NB_API_CONVERT} api_convert)")

    agent_tasks = [asyncio.create_task(agent.run()) for agent in agents]
    await asyncio.sleep(2)

    async def director_loop():
        cycle = 0
        total_usd = 0.0
        action_map = {
            'affiliation': 'post_tweet',
            'microtask': 'solve_captcha',
            'contenu': 'write_article',
            'arbitrage': 'scan_free_offers',
            'staking': 'stake_bnb',
            'api_creator': 'create_api_key',
            'hub_broker': 'match_orders',
            'direction': 'decide_strategy',
            'finance': 'optimize_portfolio',
            'api_convert': 'convert_to_bnb'
        }
        while True:
            cycle += 1
            type_queues = {}
            for i, ag in enumerate(agents):
                t = ag.type
                type_queues.setdefault(t, []).append(agents_queues[i])
            for t, queues in type_queues.items():
                action = action_map.get(t, 'idle')
                for q in queues:
                    await q.put({'action': action, 'params': {}})

            reports = []
            while not report_queue.empty():
                try:
                    r = report_queue.get_nowait()
                    reports.append(r)
                except asyncio.QueueEmpty:
                    break
            for r in reports:
                gain = r.get('gain', 0.0)
                total_usd += gain
                if gain > 0:
                    print(f"[Directrice] Agent {r['agent_id']} ({r['type']}) a gagné {gain:.6f} USD")
            print(f"[Cycle {cycle}] Gains cumulés USD : {total_usd:.4f}")

            # Sauvegarde de l'état pour le dashboard synchronisé
            with open('state.json', 'w') as f:
                json.dump({'cycle': cycle, 'total_earnings_usd': total_usd}, f, indent=2)

            if cycle % 60 == 0 and total_usd > 0:
                print(f"💱 Conversion de {total_usd:.2f} USD en BNB (réel si clés présentes)")
                bnb_balance = get_bnb_balance()
                new_bnb = bnb_balance + (total_usd / 520.0)
                save_wallet(new_bnb, total_usd)
                total_usd = 0.0
            await asyncio.sleep(60)

    asyncio.create_task(director_loop())
    asyncio.create_task(dashboard())
    asyncio.create_task(booster_light())
    await asyncio.gather(*agent_tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Arrêt")
