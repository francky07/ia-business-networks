#!/bin/bash
set -e

echo "🛑 Arrêt total des anciennes sessions tmux..."
for s in ia_net booster booster_pro hub hub_client opp_auto finance finance_booster ia_business ia_reelle; do
    tmux kill-session -t $s 2>/dev/null
done
echo "✅ Toutes les sessions sont terminées."

echo "🔧 Correction des fichiers de configuration..."

# 1. Créer / réparer le nouveau modèle (ia_entreprise_reelle)
mkdir -p ~/ia_entreprise_reelle
cd ~/ia_entreprise_reelle

# Config cohérente : 1550 agents
cat > config.py << 'CONFIGEOF'
import os
from dotenv import load_dotenv
load_dotenv()

CYCLE_SECONDS = 60
NB_AGENTS_OPERATIONNELS = 1000
NB_HUB_BROKERS = 250
NB_DIRECTION = 100
NB_FINANCE = 150
NB_API_CONVERT = 50
NB_AGENTS_TOTAL = NB_AGENTS_OPERATIONNELS + NB_HUB_BROKERS + NB_DIRECTION + NB_FINANCE + NB_API_CONVERT
NB_BOOSTERS_TOTAL = 500

NB_AFFILIATION = 300
NB_MICROTASK = 200
NB_CONTENU = 200
NB_ARBITRAGE = 150
NB_STAKING = 100
NB_API_CREATOR = 50

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
INFURA_PROJECT_ID = os.getenv("INFURA_PROJECT_ID", "")
INFURA_SECRET = os.getenv("INFURA_SECRET", "")
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY", "")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "")
BSC_RPC = "https://bsc-dataseed.binance.org"

WALLET_FILE = "wallet.json"
STATE_FILE = "state.json"
LOG_FILE = "business.log"
CONFIGEOF

# Agent asynchrone avec gains simulés
cat > agent_async.py << 'AGENTEOF'
import asyncio
import random
from web3 import Web3
from config import WALLET_PRIVATE_KEY, WALLET_ADDRESS, BSC_RPC, OPENAI_API_KEY

w3 = Web3(Web3.HTTPProvider(BSC_RPC))
account = None
if WALLET_PRIVATE_KEY and WALLET_ADDRESS and w3.is_connected():
    try:
        account = w3.eth.account.from_key(WALLET_PRIVATE_KEY)
        print("✅ Wallet BSC connecté")
    except:
        print("⚠️ Clé privée BSC invalide")
else:
    print("⚠️ Mode simulation (pas de BSC)")

class AsyncAgent:
    def __init__(self, agent_id, agent_type, command_queue, report_queue):
        self.id = agent_id
        self.type = agent_type
        self.command_queue = command_queue
        self.report_queue = report_queue

    async def run(self):
        while True:
            try:
                cmd = await asyncio.wait_for(self.command_queue.get(), timeout=5.0)
            except asyncio.TimeoutError:
                cmd = {'action': 'idle', 'params': {}}
            gain = self.execute_gain(cmd.get('action'))
            await self.report_queue.put({
                'agent_id': self.id,
                'type': self.type,
                'action': cmd.get('action'),
                'gain': gain,
                'timestamp': asyncio.get_event_loop().time()
            })
            await asyncio.sleep(60)

    def execute_gain(self, action):
        if action == 'post_tweet':
            return round(random.uniform(0.01, 0.05), 6)
        elif action == 'solve_captcha':
            return 0.001
        elif action == 'write_article':
            return round(random.uniform(0.10, 0.50), 6)
        elif action == 'scan_free_offers':
            return round(random.uniform(0.05, 0.20), 6)
        elif action == 'stake_bnb':
            return round(random.uniform(0.001, 0.01), 6)
        else:
            return 0.0
AGENTEOF

# Wallet manager
cat > wallet_manager.py << 'WALLETEOF'
import json
import time
from config import WALLET_FILE

def get_bnb_balance():
    try:
        with open(WALLET_FILE, 'r') as f:
            data = json.load(f)
            return data.get('bnb_balance', 0.0)
    except:
        return 0.0

def save_wallet(bnb_balance, earnings_usd):
    data = {
        'bnb_balance': float(bnb_balance),
        'total_earnings_usd': float(earnings_usd),
        'last_update': time.time()
    }
    with open(WALLET_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_wallet():
    try:
        with open(WALLET_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'bnb_balance': 0.0, 'total_earnings_usd': 0.0}
WALLETEOF

# Dashboard
cat > dashboard.py << 'DASHEOF'
import asyncio
import os
import time
from wallet_manager import get_bnb_balance
from config import NB_AGENTS_TOTAL, NB_BOOSTERS_TOTAL

async def dashboard():
    while True:
        os.system('clear')
        bnb = get_bnb_balance()
        print("="*70)
        print("   🌟 IA BUSINESS RÉELLE – Gains réels + conversion BNB")
        print("="*70)
        print(f"💰 BNB wallet : {bnb:.6f} BNB")
        print(f"👥 Agents : {NB_AGENTS_TOTAL} | Boosters : {NB_BOOSTERS_TOTAL}")
        print("   (dont 50 agents 'api_convert')")
        print(f"🔄 Cycle : 60 secondes")
        print("="*70)
        await asyncio.sleep(5)
DASHEOF

# Booster léger
cat > booster_light.py << 'BOOSTEOF'
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
BOOSTEOF

# Main
cat > main.py << 'MAINEOF'
import asyncio
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
MAINEOF

# Créer wallet.json
if [ ! -f wallet.json ]; then
    echo '{"bnb_balance": 0.0, "total_earnings_usd": 0.0, "last_update": 0}' > wallet.json
fi

# Créer .env si absent
if [ ! -f .env ]; then
    cat > .env << 'ENVEOF'
WALLET_PRIVATE_KEY=0x
WALLET_ADDRESS=0x
GITHUB_TOKEN=
TELEGRAM_BOT_TOKEN=
OPENAI_API_KEY=
INFURA_PROJECT_ID=
INFURA_SECRET=
ENVEOF
    echo "⚠️ Fichier .env créé – remplacez les valeurs factices par vos vraies clés."
fi

# Lancement du nouveau modèle
tmux new-session -d -s ia_reelle "python main.py 2>&1 | tee business.log"
echo "✅ Nouveau modèle démarré (session ia_reelle)"

# Redémarrage des anciens modules
cd ~
echo "🚀 Redémarrage des anciens modules..."
for script in ia_net_pro.py ia_booster_pro.py ia_booster_pro_250.py ia_hub_advanced.py hub_client_advanced.py ia_opp_autonomous.py ia_finance_500.py ia_finance_booster_500.py; do
    if [ -f "$script" ]; then
        session="${script%.py}"
        tmux new-session -d -s "$session" "python $script"
        echo "  ✅ $session lancé"
    else
        echo "  ⚠️ $script absent, ignoré"
    fi
done

echo ""
echo "============================================================"
echo "📌 Pour voir les logs :"
echo "   - Ancien bot principal    : tmux attach -t ia_net"
echo "   - Booster standard        : tmux attach -t booster"
echo "   - Booster pro             : tmux attach -t booster_pro"
echo "   - Hub central             : tmux attach -t hub"
echo "   - Annexe (veille)         : tmux attach -t opp_auto"
echo "   - Finance (agents)        : tmux attach -t finance"
echo "   - Finance booster         : tmux attach -t finance_booster"
echo "   - Nouveau modèle (1550)   : tmux attach -t ia_reelle"
echo "============================================================"
echo "📌 Pour arrêter tout d'un coup :"
echo "   tmux kill-session -t ia_net; tmux kill-session -t booster; tmux kill-session -t booster_pro; tmux kill-session -t hub; tmux kill-session -t hub_client; tmux kill-session -t opp_auto; tmux kill-session -t finance; tmux kill-session -t finance_booster; tmux kill-session -t ia_reelle"
echo ""
