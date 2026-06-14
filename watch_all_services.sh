#!/bin/bash
while true; do
    clear
    echo "════════════════════════════════════════════════════════════════════════════"
    echo "  🌐 IA BUSINESS – TABLEAU DE BORD COMPLET (tous services)"
    echo "════════════════════════════════════════════════════════════════════════════"
    echo "Heure : $(date)"
    echo ""
    echo "🖥️ SESSIONS TMUX ACTIVES :"
    tmux ls 2>/dev/null | awk '{print "   ✅ " $1}' || echo "   ❌ Aucune"
    echo ""
    if [ -f ~/ia_mem_pro.json ]; then
        net_cycle=$(python3 -c "import json; d=json.load(open('~/ia_mem_pro.json')); print(d.get('stats',{}).get('cycle',0))" 2>/dev/null || echo "0")
        net_actions=$(python3 -c "import json; d=json.load(open('~/ia_mem_pro.json')); print(d.get('stats',{}).get('actions',0))" 2>/dev/null || echo "0")
        net_balance=$(python3 -c "import json; d=json.load(open('~/ia_mem_pro.json')); print(d.get('last_balance',0))" 2>/dev/null || echo "0")
        echo "📌 BOT PRINCIPAL (ia_net) : cycle $net_cycle | actions $net_actions | BNB réel $net_balance"
    else echo "📌 BOT PRINCIPAL : fichier mémoire absent"; fi
    echo "📌 BOOSTERS :"
    tmux ls 2>/dev/null | grep -q booster && echo "   ✅ booster actif" || echo "   ❌ booster absent"
    tmux ls 2>/dev/null | grep -q booster_pro && echo "   ✅ booster_pro actif" || echo "   ❌ booster_pro absent"
    echo "📌 HUB :"
    tmux ls 2>/dev/null | grep -q hub && echo "   ✅ hub actif" || echo "   ❌ hub absent"
    tmux ls 2>/dev/null | grep -q hub_client && echo "   ✅ hub_client actif" || echo "   ❌ hub_client absent"
    if [ -f ~/ia_opp_mem.json ]; then
        opp_cycle=$(python3 -c "import json; d=json.load(open('~/ia_opp_mem.json')); print(d.get('stats',{}).get('cycle',0))" 2>/dev/null || echo "0")
        opp_opps=$(python3 -c "import json; d=json.load(open('~/ia_opp_mem.json')); print(len(d.get('opportunities',[])))" 2>/dev/null || echo "0")
        echo "📌 ANNEXE (opp_auto) : cycle $opp_cycle | opportunités $opp_opps"
    else echo "📌 ANNEXE : mémoire absente"; fi
    if [ -f ~/ia_mainnet_reelle/state.json ]; then
        reel_cycle=$(python3 -c "import json; d=json.load(open('~/ia_mainnet_reelle/state.json')); print(d.get('cycle',0))" 2>/dev/null || echo "0")
        reel_usd=$(python3 -c "import json; d=json.load(open('~/ia_mainnet_reelle/state.json')); print(d.get('total_earnings_usd',0))" 2>/dev/null || echo "0")
        echo "📌 MODULE RÉEL (ia_reelle) : cycle $reel_cycle | gains bruts $reel_usd USD"
    else echo "📌 MODULE RÉEL : state.json absent"; fi
    tmux ls 2>/dev/null | grep -q oeil_de_dieu && echo "📌 ŒIL DE DIEU (supervision) : actif" || echo "📌 ŒIL DE DIEU : inactif"
    if [ -f ~/ia_finance_mem.json ]; then
        fin_rev=$(python3 -c "import json; d=json.load(open('~/ia_finance_mem.json')); print(d.get('stats',{}).get('revenue',0))" 2>/dev/null || echo "0")
        echo "📌 FINANCE : revenu $fin_rev USD"
    else echo "📌 FINANCE : mémoire absente"; fi
    if [ -f ~/agence_kays/keys.json ]; then
        emails=$(python3 -c "import json; d=json.load(open('~/agence_kays/keys.json')); print(len(d.get('emails',[])))" 2>/dev/null || echo "0")
        tokens=$(python3 -c "import json; d=json.load(open('~/agence_kays/keys.json')); print(len(d.get('github_tokens',[])))" 2>/dev/null || echo "0")
        echo "📌 AGENCE DE KAYS : $emails emails, $tokens tokens GitHub"
    else echo "📌 AGENCE DE KAYS : keys.json absent"; fi
    if [ -f ~/departement_ventes/ventes.log ]; then
        last_link=$(grep "LIEN DE PAIEMENT" ~/departement_ventes/ventes.log 2>/dev/null | tail -1 | cut -d: -f2- | xargs)
        echo "📌 DERNIER LIEN PAYPAL : ${last_link:-Aucun}"
    else echo "📌 DERNIER LIEN PAYPAL : pas de log"; fi
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════"
    echo "🔄 Rafraîchi toutes les 10 secondes (Ctrl+C quitter)"
    sleep 10
done
