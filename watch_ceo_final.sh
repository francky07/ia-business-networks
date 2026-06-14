#!/bin/bash
while true; do
    if ! pgrep -f "ceo_stable_final.py" > /dev/null; then
        echo "$(date) - CEO arrêté, redémarrage" >> ~/ceo_restart.log
        tmux kill-session -t ceo_final 2>/dev/null
        tmux new-session -d -s ceo_final "python ~/ia_nexus/ceo_stable_final.py"
    fi
    sleep 30
done
