#!/bin/bash
while true; do
    clear
    echo "════════════════════════════════════════════════════════════════"
    echo "  📊 DASHBOARD SUPER PUISSANT – IA BUSINESS"
    echo "════════════════════════════════════════════════════════════════"
    echo "Heure : $(date)"
    echo ""
    echo "🖥️ SESSIONS TMUX :"
    tmux ls 2>/dev/null | awk '{print "   ✅ " $1}' || echo "   ❌ Aucune"
    echo ""
    NB=$(python3 -c "import json; print(len(json.load(open('~/agence_kays/keys.json')).get('emails',[])))" 2>/dev/null || echo "0")
    echo "📧 Emails en stock : $NB"
    REV=$(python3 -c "import json; print(json.load(open('~/ia_finance_mem.json')).get('stats',{}).get('revenue',0))" 2>/dev/null || echo "0")
    echo "💰 Revenu (24h) : $REV USD"
    LAST_LINK=$(grep "LIEN DE PAIEMENT" ~/departement_ventes/ventes.log 2>/dev/null | tail -1 | cut -d: -f2- | xargs)
    echo "🔗 Dernier lien PayPal : ${LAST_LINK:-Aucun}"
    echo ""
    echo "📡 STATUT DES NOTIFICATIONS :"
    if [ -f ~/departement_ventes/sell_emails_paypal.py ]; then
        grep -q "TELEGRAM_BOT_TOKEN = \"VOTRE_TOKEN\"" ~/departement_ventes/sell_emails_paypal.py && echo "   ⚠️ Telegram non configuré" || echo "   ✅ Telegram actif"
    fi
    echo "   🌐 GitHub Pages : https://francky07.github.io/ia-net-blog-pro/"
    echo ""
    echo "🔄 Rafraîchi toutes les 5 secondes (Ctrl+C quitter)"
    sleep 5
done
