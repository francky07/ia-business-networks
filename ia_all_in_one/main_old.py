import asyncio
import queue
from config import (NB_AFFILIATION, NB_MICROTASK, NB_CONTENU, NB_ARBITRAGE,
                    NB_STAKING, NB_API_CREATOR, NB_ACCOUNT_CREATOR)
from agents_operational import (AffiliationAgent, MicrotaskAgent, ContenuAgent,
                                ArbitrageAgent, StakingAgent, APICreatorAgent,
                                AccountCreatorAgent)
# import booster (remplacé par booster_light)  # démarre les boosters
import booster_light
from director import Director
from dashboard import dashboard

async def main():
    report_queue = asyncio.Queue()
    agents_queues = {}
    agent_id = 0

    def create_agent(cls, agent_type):
        nonlocal agent_id
        q = asyncio.Queue()
        agent = cls(agent_id, agent_type, q, report_queue)
        agents_queues[agent_id] = q
        agent_id += 1
        agent.start()
        return agent

    for _ in range(NB_AFFILIATION):
        create_agent(AffiliationAgent, 'affiliation')
    for _ in range(NB_MICROTASK):
        create_agent(MicrotaskAgent, 'microtask')
    for _ in range(NB_CONTENU):
        create_agent(ContenuAgent, 'contenu')
    for _ in range(NB_ARBITRAGE):
        create_agent(ArbitrageAgent, 'arbitrage')
    for _ in range(NB_STAKING):
        create_agent(StakingAgent, 'staking')
    for _ in range(NB_API_CREATOR):
        create_agent(APICreatorAgent, 'api_creator')
    for _ in range(NB_ACCOUNT_CREATOR):
        create_agent(AccountCreatorAgent, 'account_creator')

    print(f"✅ {agent_id} agents démarrés (sur 10000) – les boosters tournent déjà.")

    director = Director(report_queue, agents_queues)
    asyncio.create_task(director.run())
    asyncio.create_task(dashboard())
    asyncio.create_task(booster_light.booster_light())

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
