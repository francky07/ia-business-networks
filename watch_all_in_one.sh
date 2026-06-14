#!/bin/bash
while true; do
    clear
    echo "════════════════════════════════════════════════════════════════"
    echo "  📊 TABLEAU DE BORD UNIFIÉ – IA BUSINESS"
    echo "════════════════════════════════════════════════════════════════"
    echo "Heure : $(date)"
    echo ""
    echo "🖥️ SESSIONS TMUX :"
    tmux ls 2>/dev/null | awk '{print "   ✅ " $1}' || echo "   ❌ Aucune"
    echo ""
    echo "📧 EMAILS PRODUITS :"
    if [ -f ~/agence_kays/keys.json ]; then
        NB=$(python3 -c "import json; d=json.load(open('~/agence_kays/keys.json')); print(len(d.get('emails',[])))" 2>/dev/null || echo "0")
        echo "   $NB emails en attente de vente"
    else
        echo "   ⚠️ Fichier keys.json absent"
    fi
    echo ""
    echo "💰 DERNIER LIEN PAYPAL (extrait) :"
    if [ -f ~/departement_ventes/ventes.log ]; then
        LAST=$(grep "LIEN DE PAIEMENT" ~/departement_ventes/ventes.log 2>/dev/null | tail -1 | cut -d: -f2- | xargs)
        echo "   ${LAST:-Aucun lien généré}"
    else
        echo "   Pas encore de logs"
    fi
    echo ""
    echo "🛡️ ŒIL DE DIEU (auto‑réparation) :"
    if [ -f ~/depannage.log ]; then
        LAST_HEAL=$(tail -1 ~/depannage.log 2>/dev/null | cut -d']' -f2- | xargs)
        echo "   ${LAST_HEAL:-Aucune action récente}"
    else
        echo "   Pas de log"
    fi
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "🔄 Rafraîchi toutes les 10 secondes (Ctrl+C quitter)"
    sleep 10
done
