#!/bin/bash
# ============================================================
# Watch All-in-One - Version corrigée (chemins absolus)
# ============================================================
while true; do
    clear
    echo "════════════════════════════════════════════════════════════════════════════"
    echo "  🌐 WATCH ALL-IN-ONE | Cycles & Actions | État global des services"
    echo "════════════════════════════════════════════════════════════════════════════"
    echo "⏱️  $(date)"
    echo ""

    # --- ia_net ---
    if [ -f "$HOME/ia_mem_pro.json" ]; then
        net_cycle=$(python3 -c "import json, os; d=json.load(open(os.path.expanduser('~/ia_mem_pro.json'))); print(d.get('stats',{}).get('cycle',0))")
        net_actions=$(python3 -c "import json, os; d=json.load(open(os.path.expanduser('~/ia_mem_pro.json'))); print(d.get('stats',{}).get('actions',0))")
        net_balance=$(python3 -c "import json, os; d=json.load(open(os.path.expanduser('~/ia_mem_pro.json'))); print(d.get('last_balance',0))")
    else
        net_cycle=0; net_actions=0; net_balance=0
    fi

    # --- ia_reelle ---
    if [ -f "$HOME/ia_mainnet_reelle/state.json" ]; then
        reel_cycle=$(python3 -c "import json, os; d=json.load(open(os.path.expanduser('~/ia_mainnet_reelle/state.json'))); print(d.get('cycle',0))")
        reel_usd=$(python3 -c "import json, os; d=json.load(open(os.path.expanduser('~/ia_mainnet_reelle/state.json'))); print(d.get('total_earnings_usd',0))")
    else
        reel_cycle=0; reel_usd=0
    fi
    if [ -f "$HOME/ia_mainnet_reelle/wallet.json" ]; then
        reel_bnb=$(python3 -c "import json, os; d=json.load(open(os.path.expanduser('~/ia_mainnet_reelle/wallet.json'))); print(d.get('bnb_balance',0))")
    else
        reel_bnb=0
    fi

    # --- opp_auto ---
    if [ -f "$HOME/ia_opp_mem.json" ]; then
        opp_cycle=$(python3 -c "import json, os; d=json.load(open(os.path.expanduser('~/ia_opp_mem.json'))); print(d.get('stats',{}).get('cycle',0))")
        opp_opps=$(python3 -c "import json, os; d=json.load(open(os.path.expanduser('~/ia_opp_mem.json'))); print(len(d.get('opportunities',[])))")
    else
        opp_cycle=0; opp_opps=0
    fi

    # État des sessions tmux
    sessions=$(tmux ls 2>/dev/null | awk '{print $1}' | sed 's/://' | tr '\n' ' ')

    # --- Affichage ---
    echo "📌 BOT PRINCIPAL (ia_net) :"
    echo "   Cycle : $net_cycle   | Actions : $net_actions   | BNB réel : $net_balance"
    echo ""
    echo "📌 MODULE RÉEL (ia_reelle) :"
    echo "   Cycle : $reel_cycle   | Gains USD : $reel_usd   | BNB converti : $reel_bnb"
    echo ""
    echo "📌 ANNEXE (opp_auto) :"
    echo "   Cycle : $opp_cycle   | Opportunités : $opp_opps"
    echo ""

    booster_status=$(tmux ls 2>/dev/null | grep -c booster || echo "0")
    hub_status=$(tmux ls 2>/dev/null | grep -c hub || echo "0")
    echo "📌 AUTRES SERVICES :"
    echo "   Boosters actifs : $booster_status   | Hub actif : $hub_status"
    echo ""

    echo "🖥️ SESSIONS TMUX ACTIVES :"
    if [ -n "$sessions" ]; then
        echo "   $sessions"
    else
        echo "   (aucune)"
    fi
    echo ""

    total_cycle=$((net_cycle + reel_cycle + opp_cycle))
    total_actions=$((net_actions))
    total_balance=$(echo "$net_balance + $reel_bnb" | bc 2>/dev/null || echo "0")
    echo "📈 SYNTHÈSE GLOBALE :"
    echo "   Cycles totaux : $total_cycle   | Actions totales : $total_actions   | BNB total : $total_balance"
    echo ""

    echo "════════════════════════════════════════════════════════════════════════════"
    echo "🔄 Rafraîchi toutes les 10 secondes (Ctrl+C pour quitter)"
    sleep 10
done
