#!/data/data/com.termux/files/usr/bin/bash
# Surveillance instantanée IA NetSolutions PRO

clear
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║        IA NetSolutions PRO - Tableau de bord instantané             ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
date
echo ""

# Cycles et actions
CYCLE=$(python -c "import json; d=open('ia_mem_pro.json').read(); data=json.loads(d); print(data['stats'].get('cycle',0))" 2>/dev/null)
ACTIONS=$(python -c "import json; d=open('ia_mem_pro.json').read(); data=json.loads(d); print(data['stats'].get('actions',0))" 2>/dev/null)
ERRORS=$(python -c "import json; d=open('ia_mem_pro.json').read(); data=json.loads(d); print(len(data.get('errors',[])))" 2>/dev/null)
echo "📊 CYCLE : $CYCLE  |  ACTIONS : $ACTIONS  |  ERREURS : $ERRORS"
echo ""

# Solde BNB
BAL=$(python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')); bal=w3.from_wei(w3.eth.get_balance('0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363'), 'ether'); print(f'{bal:.8f}')" 2>/dev/null)
echo "💰 SOLDE BNB : $BAL"
echo ""

# Dernières lignes des logs
echo "📌 BOT PRINCIPAL (dernières 5 lignes) :"
tmux capture-pane -pt ia_net -S -5 2>/dev/null | tail -5 | sed 's/^/   /' || echo "   Session ia_net introuvable"
echo ""
echo "📌 AGENTS Pi (dernières 5 lignes) :"
tmux capture-pane -pt pi_agents -S -5 2>/dev/null | tail -5 | sed 's/^/   /' || echo "   Session pi_agents introuvable"
echo ""
echo "📌 BOOSTER (dernières 5 lignes) :"
tmux capture-pane -pt booster -S -5 2>/dev/null | tail -5 | sed 's/^/   /' || echo "   Session booster introuvable"
echo ""

# Services
echo "🛡️ SERVICES :"
TOKEN=$(grep '^GITHUB_TOKEN' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
if [ -n "$TOKEN" ]; then
    curl -s -H "Authorization: token $TOKEN" https://api.github.com/user > /dev/null && echo "   🐙 GitHub : ✅" || echo "   🐙 GitHub : ❌"
else
    echo "   🐙 GitHub : ⚠️"
fi
BOT=$(grep '^TELEGRAM_BOT_TOKEN' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
if [ -n "$BOT" ]; then
    curl -s "https://api.telegram.org/bot${BOT}/getMe" | grep -q '"ok":true' && echo "   📡 Telegram : ✅" || echo "   📡 Telegram : ❌"
else
    echo "   📡 Telegram : ⚠️"
fi
KEY=$(grep '^OPENAI_API_KEY' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
if [ -n "$KEY" ]; then
    curl -s -H "Authorization: Bearer $KEY" https://api.openai.com/v1/models > /dev/null && echo "   🤖 OpenAI : ✅" || echo "   🤖 OpenAI : ❌"
else
    echo "   🤖 OpenAI : ⚠️"
fi
INFURA_KEY=$(grep '^INFURA_KEY=' ~/ia_web/.env 2>/dev/null | cut -d'=' -f2)
if [ -n "$INFURA_KEY" ]; then
else
fi
PI_KEY=$(grep '^PI_API_KEY=' ~/ia_web/.env 2>/dev/null | cut -d'=' -f2)
if [ -n "$PI_KEY" ]; then
    curl -s -H "Authorization: Key $PI_KEY" https://api.minepi.com/v2/apps > /dev/null && echo "   🥧 Pi API : ✅" || echo "   🥧 Pi API : ❌"
else
    echo "   🥧 Pi API : ⚠️"
fi
echo ""

# Processus
echo "🖥️ PROCESSUS :"
pgrep -f "ia_net_pro.py" > /dev/null && echo "   ✅ Bot principal : actif" || echo "   ❌ Bot principal : arrêté"
pgrep -f "ia_pi_agents.py" > /dev/null && echo "   ✅ Agents Pi : actifs" || echo "   ❌ Agents Pi : arrêtés"
pgrep -f "ia_booster_pro.py" > /dev/null && echo "   ✅ Booster : actif" || echo "   ❌ Booster : arrêté"
pgrep -f "pi_backend.py" > /dev/null && echo "   ✅ Backend Pi : actif" || echo "   ❌ Backend Pi : arrêté"
echo ""

# Dernière sauvegarde
LAST_BACKUP=$(ls -td backup_* 2>/dev/null | head -1)
if [ -n "$LAST_BACKUP" ]; then
    echo "💾 DERNIÈRE SAUVEGARDE : $LAST_BACKUP"
else
    echo "💾 Aucune sauvegarde trouvée"
fi

echo ""
echo "🔄 Rafraîchi toutes les 5 secondes (Ctrl+C pour quitter)"
