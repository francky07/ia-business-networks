#!/bin/bash
while true; do
    clear
    echo "════════════════════════════════════════════════════════════════"
    echo "  🧠 CEREBRUM MAXIMUS – TABLEAU DE BORD GÉANT"
    echo "════════════════════════════════════════════════════════════════"
    echo "Heure : $(date)"
    echo ""
    # État du cerveau
    if pgrep -f "cerebrum_maximus.py" > /dev/null; then
        echo "✅ Cerveau actif (PID $(pgrep -f cerebrum_maximus.py))"
    else
        echo "❌ Cerveau arrêté"
    fi
    # Nombre d'emails
    NB=$(python3 -c "import json; print(len(json.load(open('~/agence_kays/keys.json')).get('emails',[])))" 2>/dev/null || echo "?")
    echo "📧 Emails en stock : $NB"
    # Dernières décisions
    echo ""
    echo "📋 DERNIÈRES DÉCISIONS :"
    tail -12 ~/cerebrum/logs/cerebrum.log 2>/dev/null | grep -E "Décision|DASHBOARD|Apprentissage" | tail -6 | sed 's/^/   /'
    # Seuils actuels
    SEUIL_VENTE=$(python3 -c "import json; print(json.load(open('~/cerebrum/memory/decisions.json')).get('seuils',{}).get('vente_emails',5))" 2>/dev/null)
    echo ""
    echo "⚙️ SEUIL DE VENTE ACTUEL : $SEUIL_VENTE emails"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "🔄 Rafraîchi toutes les 4 secondes (Ctrl+C quitter)"
    sleep 4
done
