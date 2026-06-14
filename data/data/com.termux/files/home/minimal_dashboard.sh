#!/bin/bash
while true; do
    clear
    echo "════════════════════════════════════════════════════════════════"
    echo "  📊 DASHBOARD IA BUSINESS – Tous les bots"
    echo "════════════════════════════════════════════════════════════════"
    echo "Heure : $(date)"
    NB=$(python3 -c "import json; print(len(json.load(open('~/agence_kays/keys.json')).get('emails',[])))" 2>/dev/null || echo "0")
    echo "📧 Emails : $NB"
    REVENU=$(python3 -c "import json; print(json.load(open('~/ia_finance_mem.json')).get('stats',{}).get('revenue',0))" 2>/dev/null || echo "0")
    echo "💰 Revenu : $REVENU USD"
    echo ""
    echo "🖥️ Sessions tmux :"
    tmux ls 2>/dev/null || echo "   Aucune"
    echo ""
    sleep 5
done
