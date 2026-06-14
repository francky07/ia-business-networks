#!/bin/bash
while true; do
    clear
    echo "════════════════════════════════════════════════════════════════"
    echo "  🌐 IA BUSINESS – TABLEAU DE BORD CENTRAL"
    echo "════════════════════════════════════════════════════════════════"
    echo "Heure : $(date)"
    echo ""
    echo "🖥️ SESSIONS TMUX ACTIVES :"
    tmux ls 2>/dev/null | awk '{print "   ✅ " $1}' || echo "   ❌ Aucune"
    echo ""
    echo "💰 AGENCE DE KAYS (production) :"
    if [ -f ~/agence_kays/keys.json ]; then
        emails=$(python3 -c "import json; d=json.load(open('~/agence_kays/keys.json')); print(len(d.get('emails',[])))" 2>/dev/null || echo "0")
        tokens=$(python3 -c "import json; d=json.load(open('~/agence_kays/keys.json')); print(len(d.get('github_tokens',[])))" 2>/dev/null || echo "0")
        echo "   Emails : $emails | Tokens GitHub : $tokens"
    else
        echo "   ⚠️ Pas de données"
    fi
    echo ""
    echo "💰 DÉPARTEMENT VENTES :"
    if [ -f ~/departement_ventes/wallet.json ]; then
        bnb=$(python3 -c "import json; d=json.load(open('~/departement_ventes/wallet.json')); print(d.get('bnb_balance',0))" 2>/dev/null || echo "0")
        usd=$(python3 -c "import json; d=json.load(open('~/departement_ventes/ventes_memory.json')); print(d.get('total_earned',0))" 2>/dev/null || echo "0")
        echo "   Total gagné (USD) : $usd | BNB converti : $bnb"
    else
        echo "   ⚠️ Pas de données"
    fi
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "🔄 Rafraîchi toutes les 10 secondes (Ctrl+C quitter)"
    sleep 10
done
