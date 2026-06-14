#!/bin/bash
while true; do
    clear
    echo "📊 IA NEXUS – PERFORMANCES"
    NB=$(sqlite3 ~/ia_shared/db/nexus.db "SELECT COUNT(*) FROM emails WHERE vendu=0;" 2>/dev/null || echo "0")
    REV=$(sqlite3 ~/ia_shared/db/nexus.db "SELECT COALESCE(SUM(montant),0) FROM ventes;" 2>/dev/null || echo "0")
    echo "📧 Emails stock: $NB | 💰 Revenu: $REV USD"
    tmux ls 2>/dev/null
    sleep 10
done
