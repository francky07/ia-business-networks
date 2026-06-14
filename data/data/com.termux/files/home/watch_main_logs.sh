#!/bin/bash
echo "════════════════════════════════════════════════════════════════"
echo "  📜 LOGS PRINCIPAUX (mise à jour toutes les 3 secondes)"
echo "════════════════════════════════════════════════════════════════"
echo "Heure : $(date)"
echo ""
while true; do
    clear
    echo "════════════════════════════════════════════════════════════════"
    echo "  🧠 CEREBRUM (dernières lignes)"
    tail -5 ~/cerebrum/logs/cerebrum.log 2>/dev/null || echo "   (aucun log)"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  🧠 NEXUS_BRAIN (dernières lignes)"
    tail -5 ~/nexus_brain.log 2>/dev/null || echo "   (aucun log)"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  💰 VENTES (dernières lignes)"
    tail -5 ~/departement_ventes/ventes.log 2>/dev/null || echo "   (aucun log)"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  🤖 IA_NET (dernières lignes)"
    tail -5 ~/ia_net.log 2>/dev/null || echo "   (aucun log)"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "🔄 Rafraîchi toutes les 3 secondes (Ctrl+C quitter)"
    sleep 3
done
