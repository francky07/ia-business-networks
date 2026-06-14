#!/data/data/com.termux/files/usr/bin/bash
clear
echo "=== IA NetSolutions - Épisodes, Actions & Tâches ==="
date
echo ""
CYCLE=$(python -c "import json; d=open('ia_mem.json').read(); data=json.loads(d); print(data['stats'].get('cycle',0))" 2>/dev/null)
ACTIONS=$(python -c "import json; d=open('ia_mem.json').read(); data=json.loads(d); print(data['stats'].get('actions',0))" 2>/dev/null)
echo "📊 Épisode (cycle) actuel : $CYCLE"
echo "🔢 Total des actions : $ACTIONS"
echo ""
echo "📌 Dernière action détectée (logs) :"
tmux capture-pane -pt ia_net -S -10 2>/dev/null | grep -E "Blog|Telegram|SaaS|Cycle|action" | tail -3 | sed 's/^/   /'
echo ""
echo "📋 Tâches récentes des agents :"
tmux capture-pane -pt ia_net -S -20 2>/dev/null | grep -E "\[[A-Z0-9]+\]" | tail -5 | sed 's/^/   /'
