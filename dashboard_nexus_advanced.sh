#!/bin/bash
while true; do
    clear
    echo "════════════════════════════════════════════════════════════════"
    echo "  📊 IA NEXUS – PERFORMANCES AVANCÉES"
    echo "════════════════════════════════════════════════════════════════"
    echo "Heure : $(date)"
    echo ""
    TOTAL=$(sqlite3 ~/ia_shared/db/nexus.db "SELECT COUNT(*) FROM emails;" 2>/dev/null || echo "0")
    VENDUS=$(sqlite3 ~/ia_shared/db/nexus.db "SELECT COUNT(*) FROM emails WHERE vendu=1;" 2>/dev/null || echo "0")
    STOCK=$(sqlite3 ~/ia_shared/db/nexus.db "SELECT COUNT(*) FROM emails WHERE vendu=0;" 2>/dev/null || echo "0")
    REVENU=$(sqlite3 ~/ia_shared/db/nexus.db "SELECT COALESCE(SUM(montant),0) FROM ventes;" 2>/dev/null || echo "0")
    LEADS=$(sqlite3 ~/ia_shared/db/nexus.db "SELECT COUNT(*) FROM leads;" 2>/dev/null || echo "0")
    echo "📧 EMAILS : Total=$TOTAL, Vendus=$VENDUS, Stock=$STOCK"
    echo "💰 REVENU TOTAL : $REVENU USD"
    echo "👥 LEADS : $LEADS"
    echo ""
    echo "📅 Ventes des 7 derniers jours :"
    sqlite3 ~/ia_shared/db/nexus.db "SELECT strftime('%Y-%m-%d', date, 'unixepoch') as jour, SUM(montant) FROM ventes WHERE date > strftime('%s','now','-7 days') GROUP BY jour ORDER BY jour DESC;" | while read line; do echo "   $line"; done
    echo ""
    echo "🔄 Rafraîchi toutes les 10s (Ctrl+C quitter)"
    sleep 10
done
