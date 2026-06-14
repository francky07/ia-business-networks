#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# IA NetSolutions - Tableau de bord complet (All-in-One)
# Utilisation : ./dashboard.sh   ou   watch -n 5 ./dashboard.sh
# ============================================================

while true; do
    clear
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                 IA NetSolutions PRO - Tableau de bord                ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    date
    echo ""

    # ---- 1. Statistiques principales ----
    CYCLE=$(python -c "import json; d=open('ia_mem_pro.json').read(); data=json.loads(d); print(data['stats'].get('cycle',0))" 2>/dev/null)
    ACTIONS=$(python -c "import json; d=open('ia_mem_pro.json').read(); data=json.loads(d); print(data['stats'].get('actions',0))" 2>/dev/null)
    ERRORS=$(python -c "import json; d=open('ia_mem_pro.json').read(); data=json.loads(d); print(len(data.get('errors',[])))" 2>/dev/null)
    echo "📊 CYCLE : $CYCLE  |  ACTIONS : $ACTIONS  |  ERREURS : $ERRORS"
    echo ""

    # ---- 2. Solde BNB ----
    BAL=$(python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')); bal=w3.from_wei(w3.eth.get_balance('0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363'), 'ether'); print(f'{bal:.8f}')" 2>/dev/null)
    echo "💰 SOLDE BNB : $BAL"
    echo ""

    # ---- 3. Logs des différents composants (10 dernières lignes chacun) ----
    echo "📌 BOT PRINCIPAL (ia_net) :"
    tmux capture-pane -pt ia_net -S -10 2>/dev/null | tail -10 || echo "   Session absente"
    echo ""
    echo "📌 BOOSTER STANDARD (booster) :"
    tmux capture-pane -pt booster -S -10 2>/dev/null | tail -10 || echo "   Session absente"
    echo ""
    echo "📌 BOOSTER PRO (booster_pro) :"
    tmux capture-pane -pt booster_pro -S -10 2>/dev/null | tail -10 || echo "   Session absente"
    echo ""
    echo "📌 HUB (hub) :"
    tmux capture-pane -pt hub -S -10 2>/dev/null | tail -10 || echo "   Session absente"
    echo ""
    echo "📌 ANNEXE (opp_auto) :"
    tmux capture-pane -pt opp_auto -S -10 2>/dev/null | tail -10 || echo "   Session absente"
    echo ""

    # ---- 4. État des services (GitHub, Telegram, OpenAI) ----
    echo "🛡️ SERVICES :"
    # GitHub
    TOKEN=$(grep '^GITHUB_TOKEN' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
    if [ -n "$TOKEN" ]; then
        curl -s -H "Authorization: token $TOKEN" https://api.github.com/user > /dev/null && echo "   🐙 GitHub : ✅" || echo "   🐙 GitHub : ❌"
    else
        echo "   🐙 GitHub : ⚠️"
    fi
    # Telegram
    BOT=$(grep '^TELEGRAM_BOT_TOKEN' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
    if [ -n "$BOT" ]; then
        curl -s "https://api.telegram.org/bot${BOT}/getMe" | grep -q '"ok":true' && echo "   📡 Telegram : ✅" || echo "   📡 Telegram : ❌"
    else
        echo "   📡 Telegram : ⚠️"
    fi
    # OpenAI
    KEY=$(grep '^OPENAI_API_KEY' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
    if [ -n "$KEY" ]; then
        curl -s -H "Authorization: Bearer $KEY" https://api.openai.com/v1/models > /dev/null && echo "   🤖 OpenAI : ✅" || echo "   🤖 OpenAI : ❌"
    else
        echo "   🤖 OpenAI : ⚠️"
    fi
    echo ""

    # ---- 5. Processus actifs ----
    echo "🖥️ PROCESSUS :"
    for p in ia_net_pro.py ia_booster_pro.py ia_booster_pro_250.py hub_client_advanced.py ia_opp_autonomous.py; do
        if pgrep -f "$p" > /dev/null; then
            echo "   ✅ $p"
        else
            echo "   ❌ $p"
        fi
    done
    echo ""

    # ---- 6. Dernières erreurs ----
    echo "⚠️ DERNIÈRES ERREURS (ia_mem_pro.json) :"
    python -c "import json; d=open('ia_mem_pro.json').read(); data=json.loads(d); err=data.get('errors', []); print('\n'.join([f'   {e[:100]}' for e in err[-3:]]))" 2>/dev/null || echo "   Aucune erreur"
    echo ""

    echo "🔄 Rafraîchi toutes les 5 secondes (Ctrl+C pour quitter)"
    sleep 5
done
