#!/bin/bash
tmux kill-session -t oeil_de_dieu 2>/dev/null
pkill -f "oeil_de_dieu" 2>/dev/null
echo "✅ L'Œil de Dieu arrêté."
