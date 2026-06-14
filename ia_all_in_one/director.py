import asyncio
import time
import random
from collections import defaultdict
from config import CYCLE_SECONDS, NB_AGENTS_TOTAL
from wallet_manager import get_bnb_balance, save_wallet

class Director:
    def __init__(self, report_queue, agents_queues):
        self.report_queue = report_queue
        self.agents_queues = agents_queues
        self.cycle = 0
        self.strategy_performance = defaultdict(float)
        self.action_counts = defaultdict(int)
        self.total_earnings_usd = 0.0

    async def run(self):
        print("🧠 IA Directrice démarrée – 10k agents, cycle 60s")
        while True:
            start = time.time()
            self.cycle += 1
            reports = await self.collect_reports()
            for r in reports:
                gain = r.get('gain', 0.0)
                action = r.get('action', 'unknown')
                self.strategy_performance[action] += gain
                self.action_counts[action] += 1
                self.total_earnings_usd += gain

            if self.cycle % 60 == 0 and self.total_earnings_usd > 0:
                print(f"💱 Conversion de {self.total_earnings_usd:.2f} USD en BNB (simulée)")
                bnb_balance = get_bnb_balance() + (self.total_earnings_usd / 520)
                save_wallet(bnb_balance, self.total_earnings_usd)
                self.total_earnings_usd = 0.0

            allocation = self.decide_allocation()
            await self.send_commands(allocation)
            save_wallet(get_bnb_balance(), self.total_earnings_usd)

            elapsed = time.time() - start
            await asyncio.sleep(max(0, CYCLE_SECONDS - elapsed))

    async def collect_reports(self):
        reports = []
        while not self.report_queue.empty():
            try:
                reports.append(self.report_queue.get_nowait())
            except asyncio.QueueEmpty:
                break
        return reports

    def decide_allocation(self):
        if not self.strategy_performance:
            return {
                'post_tweet': 2000,
                'solve_captcha': 2000,
                'write_article': 1500,
                'scan_free_offers': 1500,
                'stake_bnb': 1000,
                'create_github_token': 1000,
                'create_email': 1000
            }
        roi = {}
        for act, total in self.strategy_performance.items():
            count = self.action_counts.get(act, 1)
            roi[act] = total / count
        if not roi:
            return {}
        best = max(roi, key=roi.get)
        total_ops = NB_AGENTS_TOTAL
        alloc = {best: int(0.6 * total_ops)}
        remaining = total_ops - alloc[best]
        others = [a for a in roi if a != best][:5]
        if others:
            per = remaining // len(others)
            for a in others:
                alloc[a] = per
        return alloc

    async def send_commands(self, allocation):
        action_list = []
        for act, count in allocation.items():
            action_list.extend([act] * count)
        while len(action_list) < len(self.agents_queues):
            action_list.append('idle')
        random.shuffle(action_list)
        for i, (agent_id, q) in enumerate(self.agents_queues.items()):
            action = action_list[i] if i < len(action_list) else 'idle'
            expected = self.get_expected_gain(action)
            await q.put({'action': action, 'params': {}, 'expected_gain': expected})

    def get_expected_gain(self, action):
        gains = {
            'post_tweet': 0.02,
            'solve_captcha': 0.0005,
            'write_article': 0.05,
            'scan_free_offers': 0.1,
            'stake_bnb': 0.003,
            'create_github_token': 0.0,
            'create_email': 0.0,
            'idle': 0.0
        }
        return gains.get(action, 0.001)
