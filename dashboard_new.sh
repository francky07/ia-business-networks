#!/data/data/com.termux/files/usr/bin/bash
while true; do
    clear
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║              IA NetSolutions PRO - Tableau de bord                    ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    date
    echo ""

    CYCLE=$(python -c "import json; d=open('ia_mem_pro.json').read(); data=json.loads(d); print(data['stats'].get('cycle',0))" 2>/dev/null)
    ACTIONS=$(python -c "import json; d=open('ia_mem_pro.json').read(); data=json.loads(d); print(data['stats'].get('actions',0))" 2>/dev/null)
    ERRORS=$(python -c "import json; d=open('ia_mem_pro.json').read(); data=json.loads(d); print(len(data.get('errors',[])))" 2>/dev/null)
    echo "📊 CYCLE : $CYCLE  |  ACTIONS : $ACTIONS  |  ERREURS : $ERRORS"
    echo ""

    BAL=$(python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')); bal=w3.from_wei(w3.eth.get_balance('0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363'), 'ether'); print(f'{bal:.8f}')" 2>/dev/null)
    echo "💰 SOLDE BNB : $BAL"
    echo ""

    echo "📌 BOT PRINCIPAL (dernières 10 lignes) :"
    tmux capture-pane -pt ia_net -S -10 2>/dev/null | tail -10 || echo "   Session ia_net introuvable"
    echo ""
    echo "📌 BOOSTER (dernières 10 lignes) :"
    tmux capture-pane -pt booster -S -10 2>/dev/null | tail -10 || echo "   Session booster introuvable"
    echo ""

    echo "🛡️ SERVICES :"
    TOKEN=$(grep '^GITHUB_TOKEN' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
    [ -n "$TOKEN" ] && curl -s -H "Authorization: token $TOKEN" https://api.github.com/user > /dev/null && echo "   🐙 GitHub : ✅" || echo "   🐙 GitHub : ❌"
    BOT=$(grep '^TELEGRAM_BOT_TOKEN' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
    [ -n "$BOT" ] && curl -s "https://api.telegram.org/bot${BOT}/getMe" | grep -q '"ok":true' && echo "   📡 Telegram : ✅" || echo "   📡 Telegram : ❌"
    KEY=$(grep '^OPENAI_API_KEY' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
    [ -n "$KEY" ] && curl -s -H "Authorization: Bearer $KEY" https://api.openai.com/v1/models > /dev/null && echo "   🤖 OpenAI : ✅" || echo "   🤖 OpenAI : ❌"
    echo ""

    echo "🖥️ PROCESSUS :"
    pgrep -f "ia_net_pro.py" > /dev/null && echo "   ✅ Bot principal : actif" || echo "   ❌ Bot principal : arrêté"
    pgrep -f "ia_booster_pro.py" > /dev/null && echo "   ✅ Booster : actif" || echo "   ❌ Booster : arrêté"
    echo ""

    LAST_BACKUP=$(ls -td backup_* 2>/dev/null | head -1)
    [ -n "$LAST_BACKUP" ] && echo "💾 DERNIÈRE SAUVEGARDE : $LAST_BACKUP" || echo "💾 Aucune sauvegarde"
    echo ""
    echo "🔄 Rafraîchi toutes les 5 secondes (Ctrl+C pour quitter)"
    sleep 5
done
