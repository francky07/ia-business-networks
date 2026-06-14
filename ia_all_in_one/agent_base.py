import threading
import time
from config import CYCLE_SECONDS

class BaseAgent(threading.Thread):
    def __init__(self, agent_id, agent_type, command_queue, report_queue):
        super().__init__(daemon=True)
        self.id = agent_id
        self.type = agent_type
        self.command_queue = command_queue
        self.report_queue = report_queue
        self.running = True

    def run(self):
        while self.running:
            try:
                cmd = self.command_queue.get(timeout=1)
            except:
                cmd = self.default_command()
            gain = self.execute(cmd.get('action', 'idle'), cmd.get('params', {}))
            self.report_queue.put({
                'agent_id': self.id,
                'type': self.type,
                'action': cmd.get('action'),
                'gain': gain,
                'timestamp': time.time()
            })
            time.sleep(CYCLE_SECONDS)

    def execute(self, action, params):
        return 0.0

    def default_command(self):
        return {'action': 'idle', 'params': {}}
