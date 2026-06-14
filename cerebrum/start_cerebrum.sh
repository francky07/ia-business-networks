#!/bin/bash
tmux kill-session -t cerebrum 2>/dev/null
cd ~/cerebrum/brain
tmux new-session -d -s cerebrum "python cerebrum_maximus.py"
echo "🧠 Cerveau géant lancé dans session tmux 'cerebrum'"
echo "   Pour voir les logs : tmux attach -t cerebrum"
echo "   Pour suivre les décisions : tail -f ~/cerebrum/logs/cerebrum.log"
