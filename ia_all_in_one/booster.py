import threading
import subprocess
import time
import json
from config import NB_BOOSTERS_TOTAL, WALLET_FILE

class Booster(threading.Thread):
    def __init__(self, booster_id, role, interval=60):
        super().__init__(daemon=True)
        self.id = booster_id
        self.role = role
        self.interval = interval
        self.last_run = 0

    def run(self):
        while True:
            now = time.time()
            if now - self.last_run >= self.interval:
                self.last_run = now
                self.execute()
            time.sleep(5)

    def execute(self):
        if self.role == 'process_supervisor':
            if not self.is_running("main.py"):
                subprocess.Popen(["python", "main.py"])
        elif self.role == 'revenue_monitor':
            try:
                with open(WALLET_FILE) as f:
                    data = json.load(f)
                    print(f"[Booster {self.id}] BNB: {data.get('bnb_balance',0):.6f} | USD: {data.get('total_earnings_usd',0):.2f}")
            except:
                pass
        elif self.role == 'api_health':
            pass
        elif self.role == 'optimizer':
            pass

    def is_running(self, script):
        try:
            result = subprocess.run(["pgrep", "-f", script], capture_output=True)
            return result.returncode == 0
        except:
            return False

roles = ['process_supervisor', 'revenue_monitor', 'api_health', 'optimizer']
for i in range(NB_BOOSTERS_TOTAL):
    role = roles[i % len(roles)]
    booster = Booster(i, role, interval=60)
    booster.start()
