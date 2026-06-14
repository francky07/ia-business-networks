import asyncio
import random
from config import CYCLE_SECONDS

class AsyncAgent:
    def __init__(self, agent_id, agent_type, command_queue, report_queue):
        self.id = agent_id
        self.type = agent_type
        self.command_queue = command_queue
        self.report_queue = report_queue

    async def run(self):
        while True:
            try:
                # Attendre une commande (timeout 5s pour éviter de bloquer)
                cmd = await asyncio.wait_for(self.command_queue.get(), timeout=5.0)
                print(f"[Agent {self.id}] Commande reçue: {cmd.get('action')}")
            except asyncio.TimeoutError:
                cmd = {'action': 'idle', 'params': {}}
                print(f"[Agent {self.id}] Timeout → idle")
            gain = self.execute(cmd.get('action'), cmd.get('params', {}))
            if gain > 0:
                print(f"[Agent {self.id}] Gain: {gain:.6f} USD")
            await self.report_queue.put({
                'agent_id': self.id,
                'type': self.type,
                'action': cmd.get('action'),
                'gain': gain,
                'timestamp': asyncio.get_event_loop().time()
            })
            await asyncio.sleep(CYCLE_SECONDS)

    def execute(self, action, params):
        if action == 'post_tweet':
            return round(random.uniform(0.01, 0.05), 6)
        elif action == 'solve_captcha':
            return 0.001
        elif action == 'write_article':
            return round(random.uniform(0.1, 0.5), 6)
        elif action == 'scan_free_offers':
            return round(random.uniform(0.05, 0.2), 6)
        elif action == 'stake_bnb':
            return round(random.uniform(0.001, 0.01), 6)
        else:
            return 0.0
