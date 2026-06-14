#!/data/data/com.termux/files/usr/bin/bash
clear
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║         IA NetSolutions - Suivi avancé (cycles, actions, objectif)       ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
date
echo ""

# --- 1. Cycles et actions ---
CYCLE=$(python -c "import json; d=open('ia_mem.json').read(); data=json.loads(d); print(data['stats'].get('cycle',0))" 2>/dev/null)
ACTIONS=$(python -c "import json; d=open('ia_mem.json').read(); data=json.loads(d); print(data['stats'].get('actions',0))" 2>/dev/null)
echo "📊 CYCLE ACTUEL : $CYCLE"
echo "🔢 ACTIONS TOTALES : $ACTIONS"
echo ""

# --- 2. Solde BNB et objectif 1 milliard ---
BAL=$(python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')); bal=w3.from_wei(w3.eth.get_balance('0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363'), 'ether'); print(bal)" 2>/dev/null)
if [ -n "$BAL" ]; then
    echo "💰 SOLDE BNB : $BAL"
    OBJECTIF=1000000000
    PROGRESS=$(echo "scale=10; $BAL * 600 / $OBJECTIF * 100" | bc 2>/dev/null) # approx 600 USD/BNB
    echo "🎯 OBJECTIF 1 MILLIARD $ : ${PROGRESS}%"
else
    echo "💰 SOLDE BNB : indisponible"
fi
echo ""

# --- 3. Dernière action détectée (Blog, Telegram, SaaS) ---
LAST_ACTION=$(tmux capture-pane -pt ia_net -S -20 2>/dev/null | grep -E "Blog|Telegram|SaaS" | tail -1 | sed 's/^[ \t]*//')
if [ -n "$LAST_ACTION" ]; then
    echo "📌 DERNIÈRE ACTION : $LAST_ACTION"
else
    echo "📌 DERNIÈRE ACTION : aucune récente"
fi
echo ""

# --- 4. Tâches récentes des agents (5 dernières lignes d'agents) ---
echo "📋 TÂCHES RÉCENTES (agents) :"
tmux capture-pane -pt ia_net -S -25 2>/dev/null | grep -E "\[[A-Z0-9]+\]" | tail -5 | sed 's/^/   /'
echo ""

# --- 5. État des services critiques ---
echo "🛡️ SERVICES :"
TOKEN=$(grep "^GITHUB_TOKEN" ia_net.py 2>/dev/null | cut -d'"' -f2)
if [ -n "$TOKEN" ]; then
    curl -s -H "Authorization: token $TOKEN" https://api.github.com/user > /dev/null && echo "   ✅ GitHub" || echo "   ❌ GitHub"
else
    echo "   ⚠️ GitHub (token manquant)"
fi
BOT=$(grep "^TELEGRAM_BOT_TOKEN" ia_net.py 2>/dev/null | cut -d'"' -f2)
if [ -n "$BOT" ]; then
    curl -s "https://api.telegram.org/bot${BOT}/getMe" | grep -q '"ok":true' && echo "   ✅ Telegram" || echo "   ❌ Telegram"
else
    echo "   ⚠️ Telegram (non configuré)"
fi
KEY=$(grep "^OPENAI_API_KEY" ia_net.py 2>/dev/null | cut -d'"' -f2)
if [ -n "$KEY" ]; then
    curl -s -H "Authorization: Bearer $KEY" https://api.openai.com/v1/models > /dev/null && echo "   ✅ OpenAI" || echo "   ❌ OpenAI (quota)"
else
    echo "   ⚠️ OpenAI (non configuré)"
fi
echo ""

# --- 6. Progression du booster (epsilon ajusté) ---
EPSILON=$(grep "epsilon = max" ia_booster.py 2>/dev/null | tail -1 | grep -oP '0\.[0-9]+')
if [ -n "$EPSILON" ]; then
    echo "⚙️ BOOSTER : epsilon RL = $EPSILON"
else
    echo "⚙️ BOOSTER : actif (epsilon par défaut)"
fi
echo ""

# --- 7. Processus ---
pgrep -f "ia_net.py" > /dev/null && echo "🖥️ Bot principal : ✅ actif" || echo "🖥️ Bot principal : ❌ arrêté"
pgrep -f "ia_booster.py" > /dev/null && echo "🖥️ Booster : ✅ actif" || echo "🖥️ Booster : ❌ arrêté"
