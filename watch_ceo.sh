#!/bin/bash
while true; do
    if ! pgrep -f "ceo_simple.py" > /dev/null; then
        echo "$(date) - CEO arrêté, redémarrage" >> ~/ceo_restart.log
        tmux kill-session -t ceo_simple 2>/dev/null
        tmux new-session -d -s ceo_simple "python ~/ia_nexus/ceo_simple.py"
    fi
    sleep 30
done
