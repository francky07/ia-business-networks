#!/bin/bash
while true; do
    clear
    echo "════════════════════════════════════════════════════════════════"
    echo "  📜 LOGS COMPLETS – TOUS LES BOTS (rafraîchi toutes les 3s)"
    echo "════════════════════════════════════════════════════════════════"
    echo "Heure : $(date)"
    echo ""
    for s in $(tmux ls 2>/dev/null | cut -d: -f1); do
        echo "▸▸▸ SESSION : $s"
        tmux capture-pane -t "$s" -p -S -10 2>/dev/null | tail -10 | sed 's/^/   /'
        echo ""
    done
    echo "════════════════════════════════════════════════════════════════"
    echo "🔄 Ctrl+C pour quitter"
    sleep 3
done
