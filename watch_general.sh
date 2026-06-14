#!/data/data/com.termux/files/usr/bin/bash
while true; do
    clear
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║         IA NetSolutions PRO - Tableau de bord général             ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    date
    echo ""
    echo "📌 BOT PRINCIPAL (dernières 10 lignes) :"
    tmux capture-pane -pt ia_net -S -10 2>/dev/null | tail -10 || echo "   Session ia_net introuvable"
    echo ""
    echo "📌 AGENTS Pi (dernières 10 lignes) :"
    tmux capture-pane -pt pi_agents -S -10 2>/dev/null | tail -10 || echo "   Session pi_agents introuvable"
    echo ""
    echo "📌 BOOSTER (dernières 10 lignes) :"
    tmux capture-pane -pt booster -S -10 2>/dev/null | tail -10 || echo "   Session booster introuvable"
    echo ""
    echo "⛓️ BSC : $(python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')); print('✅' if w3.is_connected() else '❌')" 2>/dev/null)"
    BAL=$(python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')); bal=w3.from_wei(w3.eth.get_balance('0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363'), 'ether'); print(f'💰 {bal:.8f} BNB')" 2>/dev/null)
    echo "$BAL"
    echo ""
    echo "🛡️ SERVICES"
    TOKEN=$(grep '^GITHUB_TOKEN' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
    [ -n "$TOKEN" ] && curl -s -H "Authorization: token $TOKEN" https://api.github.com/user > /dev/null && echo "   🐙 GitHub : ✅" || echo "   🐙 GitHub : ❌"
    BOT=$(grep '^TELEGRAM_BOT_TOKEN' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
    [ -n "$BOT" ] && curl -s "https://api.telegram.org/bot${BOT}/getMe" | grep -q '"ok":true' && echo "   📡 Telegram : ✅" || echo "   📡 Telegram : ❌"
    KEY=$(grep '^OPENAI_API_KEY' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
    [ -n "$KEY" ] && curl -s -H "Authorization: Bearer $KEY" https://api.openai.com/v1/models > /dev/null && echo "   🤖 OpenAI : ✅" || echo "   🤖 OpenAI : ❌"
    echo ""
    echo "🔌 INFURA : $(python -c "import os; from dotenv import load_dotenv; load_dotenv('~/ia_web/.env'); key=os.getenv('INFURA_KEY'); from web3 import Web3; w3=Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{key}')); print('✅' if w3.is_connected() else '❌')" 2>/dev/null)"
    echo "🥧 Pi API : $(python -c "import os; from dotenv import load_dotenv; load_dotenv('~/ia_web/.env'); key=os.getenv('PI_API_KEY'); import requests; r=requests.get('https://api.minepi.com/v2/me', headers={'Authorization': f'Key {key}'}); print('✅' if r.status_code==200 else '❌')" 2>/dev/null)"
    echo ""
    echo "🖥️ PROCESSUS"
    pgrep -f "ia_net_pro.py" > /dev/null && echo "   ✅ Bot principal : actif" || echo "   ❌ Bot principal : arrêté"
    pgrep -f "ia_pi_agents.py" > /dev/null && echo "   ✅ Agents Pi : actifs" || echo "   ❌ Agents Pi : arrêtés"
    pgrep -f "ia_booster_pro.py" > /dev/null && echo "   ✅ Booster : actif" || echo "   ❌ Booster : arrêté"
    pgrep -f "pi_backend.py" > /dev/null && echo "   ✅ Backend Pi : actif" || echo "   ❌ Backend Pi : arrêté"
    echo ""
    echo "⚠️ ERREURS (mémoire) :"
    python -c "import json; d=open('ia_mem_pro.json').read(); data=json.loads(d); err=data.get('errors',[]); print('\n'.join([f'   {e[:80]}' for e in err[-3:]]))" 2>/dev/null || echo "   Aucune"
    echo ""
    echo "💾 ESPACE DISQUE : $(df -h /data | tail -1 | awk '{print $3"/"$2" ("$5")"}')"
    echo ""
    echo "🔄 Rafraîchi toutes les 5 sec (Ctrl+C quitter)"
    sleep 5
done
