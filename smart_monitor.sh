#!/data/data/com.termux/files/usr/bin/bash
while true; do
    clear
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║         IA NetSolutions - Smart Cycle Monitor                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    date
    echo ""

    # Lecture mémoire
    CYCLE=$(python -c "import json; d=open('ia_mem.json').read(); data=json.loads(d); print(data['stats'].get('cycle',0))" 2>/dev/null)
    ACTIONS=$(python -c "import json; d=open('ia_mem.json').read(); data=json.loads(d); print(data['stats'].get('actions',0))" 2>/dev/null)
    ERRORS=$(python -c "import json; d=open('ia_mem.json').read(); data=json.loads(d); print(len(data.get('errors',[])))" 2>/dev/null)
    echo "📊 CYCLE : $CYCLE | ACTIONS : $ACTIONS | ⚠️ ERREURS : $ERRORS"
    echo ""

    # Solde BNB
    BAL=$(python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')); bal=w3.from_wei(w3.eth.get_balance('0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363'), 'ether'); print(f'{bal:.8f}')" 2>/dev/null)
    echo "💰 SOLDE BNB : $BAL"
    echo ""

    # Services
    echo "🛡️ SERVICES :"
    TOKEN=$(grep "^GITHUB_TOKEN" ia_net.py 2>/dev/null | cut -d'"' -f2)
    if [ -n "$TOKEN" ]; then
        curl -s -H "Authorization: token $TOKEN" https://api.github.com/user > /dev/null 2>&1 && echo "   ✅ GitHub" || echo "   ❌ GitHub (token invalide)"
    else
        echo "   ⚠️ GitHub (token manquant)"
    fi
    BOT=$(grep "^TELEGRAM_BOT_TOKEN" ia_net.py 2>/dev/null | cut -d'"' -f2)
    if [ -n "$BOT" ]; then
        curl -s "https://api.telegram.org/bot${BOT}/getMe" | grep -q '"ok":true' 2>/dev/null && echo "   ✅ Telegram" || echo "   ❌ Telegram"
    else
        echo "   ⚠️ Telegram (non configuré)"
    fi
    KEY=$(grep "^OPENAI_API_KEY" ia_net.py 2>/dev/null | cut -d'"' -f2)
    if [ -n "$KEY" ]; then
        curl -s -H "Authorization: Bearer $KEY" https://api.openai.com/v1/models > /dev/null 2>&1 && echo "   ✅ OpenAI" || echo "   ❌ OpenAI (quota/clé)"
    else
        echo "   ⚠️ OpenAI (non configuré)"
    fi
    echo ""

    # Dernière action
    LAST_ACTION=$(tmux capture-pane -pt ia_net -S -5 2>/dev/null | grep -E "Blog|Telegram|SaaS|Cycle" | tail -1)
    if [ -n "$LAST_ACTION" ]; then
        echo "📌 DERNIÈRE ACTION : $LAST_ACTION"
    else
        echo "📌 DERNIÈRE ACTION : aucune récente (tmux absent ?)"
    fi
    echo ""

    # Actions smart
    if [ -n "$ERRORS" ] && [ "$ERRORS" -gt 5 ] 2>/dev/null; then
        echo "🔧 ACTION SMART : Trop d'erreurs ($ERRORS) → nettoyage mémoire"
        python -c "import json; d=open('ia_mem.json').read(); data=json.loads(d); data['errors']=data['errors'][-10:]; open('ia_mem.json','w').write(json.dumps(data))" 2>/dev/null
        echo "   → Mémoire nettoyée (10 dernières erreurs conservées)"
    fi
    if ! pgrep -f "ia_net.py" > /dev/null; then
        echo "🔧 ACTION SMART : Bot principal arrêté → redémarrage"
        tmux new-session -d -s ia_net "python ia_net.py" 2>/dev/null
        echo "   → Redémarrage lancé"
    fi
    if ! pgrep -f "ia_booster.py" > /dev/null; then
        echo "🔧 ACTION SMART : Booster arrêté → redémarrage"
        tmux new-session -d -s booster "python ia_booster.py" 2>/dev/null
        echo "   → Redémarrage lancé"
    fi
    echo ""
    echo "🔄 Rafraîchi toutes les 10 secondes (Ctrl+C pour quitter)"
    sleep 10
done
