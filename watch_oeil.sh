#!/bin/bash
while true; do
    clear
    echo "════════════════════════════════════════════════════════════════"
    echo "  👁️  ŒIL DE DIEU – Surveillance en temps réel"
    echo "════════════════════════════════════════════════════════════════"
    echo "Date : $(date)"
    echo ""
    if [ -f ~/oeil_de_dieu/oeil_memory.json ]; then
        cycle=$(python3 -c "import json; d=json.load(open('~/oeil_de_dieu/oeil_memory.json')); print(d.get('cycle',0))" 2>/dev/null || echo "0")
        earned=$(python3 -c "import json; d=json.load(open('~/oeil_de_dieu/oeil_memory.json')); print(d.get('total_earned',0))" 2>/dev/null || echo "0")
        emails=$(python3 -c "import json; d=json.load(open('~/oeil_de_dieu/oeil_memory.json')); print(len(d.get('emails',[])))" 2>/dev/null || echo "0")
        tokens=$(python3 -c "import json; d=json.load(open('~/oeil_de_dieu/oeil_memory.json')); print(len(d.get('github_tokens',[])))" 2>/dev/null || echo "0")
        echo "📊 Cycle : $cycle"
        echo "💰 Total gagné (USD) : $earned"
        echo "📧 Emails créés : $emails"
        echo "🔑 Tokens GitHub : $tokens"
    else
        echo "⚠️ Aucune mémoire – le bot n’a pas encore tourné"
    fi
    echo ""
    echo "🖥️ Session tmux :"
    tmux ls | grep oeil_de_dieu || echo "   ❌ Session oeil_de_dieu introuvable"
    echo ""
    echo "🔄 Rafraîchi toutes les 10 secondes (Ctrl+C quitter)"
    sleep 10
done
