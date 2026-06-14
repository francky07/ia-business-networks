#!/bin/bash
# Synchronisation des états IA Business

set -e

REAL_DIR="$HOME/ia_entreprise_reelle"
SYNC_DIR="$HOME/ia_sync"
mkdir -p "$SYNC_DIR"
SYNC_WALLET="$SYNC_DIR/wallet_aggregated.json"
SYNC_STATS="$SYNC_DIR/stats.txt"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$SYNC_DIR/sync.log"
}

collect_wallet() {
    python3 -c "
import json, os
wallet_re = {}
wallet_fi = {}
if os.path.exists('$REAL_DIR/wallet.json'):
    with open('$REAL_DIR/wallet.json') as f:
        wallet_re = json.load(f)
if os.path.exists('$HOME/wallet.json'):
    with open('$HOME/wallet.json') as f:
        wallet_fi = json.load(f)
total_bnb = wallet_re.get('bnb_balance', 0.0) + wallet_fi.get('bnb_balance', 0.0)
total_usd = wallet_re.get('total_earnings_usd', 0.0) + wallet_fi.get('total_earnings_usd', 0.0)
with open('$SYNC_WALLET', 'w') as f:
    json.dump({'bnb_balance': total_bnb, 'total_earnings_usd': total_usd, 'last_update': wallet_re.get('last_update', 0)}, f, indent=2)
print(f'✅ Synthèse wallet : {total_bnb:.6f} BNB, {total_usd:.2f} USD')
"
}

collect_stats() {
    echo "======= STATS GLOBALES =======" > "$SYNC_STATS"
    echo "Date: $(date)" >> "$SYNC_STATS"
    echo "" >> "$SYNC_STATS"

    # Nouveau modèle
    if [ -f "$REAL_DIR/state.json" ]; then
        cycle=$(python3 -c "import json; print(json.load(open('$REAL_DIR/state.json')).get('cycle', 0))")
        echo "📌 Nouveau modèle (ia_reelle) :" >> "$SYNC_STATS"
        echo "   Cycle : $cycle" >> "$SYNC_STATS"
    fi
    if [ -f "$REAL_DIR/wallet.json" ]; then
        earnings=$(python3 -c "import json; print(json.load(open('$REAL_DIR/wallet.json')).get('total_earnings_usd', 0))")
        echo "   Gains totaux USD : $earnings" >> "$SYNC_STATS"
    fi

    # Finance
    if [ -f "$HOME/ia_finance_mem.json" ]; then
        revenue=$(python3 -c "import json; print(json.load(open('$HOME/ia_finance_mem.json')).get('stats', {}).get('revenue', 0))")
        echo "📌 Finance (500 agents) :" >> "$SYNC_STATS"
        echo "   Revenu généré : $revenue USD" >> "$SYNC_STATS"
    fi

    # Bot principal ia_net
    if [ -f "$HOME/ia_mem_pro.json" ]; then
        cycle_main=$(python3 -c "import json; print(json.load(open('$HOME/ia_mem_pro.json')).get('stats', {}).get('cycle', 0))")
        actions=$(python3 -c "import json; print(json.load(open('$HOME/ia_mem_pro.json')).get('stats', {}).get('actions', 0))")
        echo "📌 Bot principal (ia_net) :" >> "$SYNC_STATS"
        echo "   Cycle : $cycle_main" >> "$SYNC_STATS"
        echo "   Actions : $actions" >> "$SYNC_STATS"
    fi

    echo "" >> "$SYNC_STATS"
    echo "🖥️ Sessions tmux actives :" >> "$SYNC_STATS"
    tmux ls 2>/dev/null | while read line; do echo "   $line" >> "$SYNC_STATS"; done || echo "   Aucune" >> "$SYNC_STATS"

    echo "" >> "$SYNC_STATS"
    echo "⚠️ Dernières erreurs :" >> "$SYNC_STATS"
    if [ -f "$REAL_DIR/business.log" ]; then
        grep -i error "$REAL_DIR/business.log" 2>/dev/null | tail -3 >> "$SYNC_STATS"
    fi
}

show_dashboard() {
    clear
    echo "============================================================"
    echo "   🌟 IA BUSINESS - SYNCHRONISATION DES ÉTATS"
    echo "============================================================"
    cat "$SYNC_STATS"
    echo "============================================================"
    if [ -f "$SYNC_WALLET" ]; then
        bnb=$(python3 -c "import json; print(json.load(open('$SYNC_WALLET')).get('bnb_balance', 0))")
        usd=$(python3 -c "import json; print(json.load(open('$SYNC_WALLET')).get('total_earnings_usd', 0))")
        echo "💰 Wallet global : $bnb BNB / $usd USD"
    fi
    echo "============================================================"
    echo "📌 Rafraîchi toutes les 10 secondes (Ctrl+C quitter)"
}

sync_loop() {
    while true; do
        collect_wallet
        collect_stats
        show_dashboard
        sleep 10
    done
}

if [ "$1" == "--once" ]; then
    collect_wallet
    collect_stats
    cat "$SYNC_STATS"
else
    sync_loop
fi
