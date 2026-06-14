#!/bin/bash
~/stop_oeil.sh
cd ~/oeil_de_dieu
tmux new-session -d -s oeil_de_dieu "python oeil_de_dieu.py"
echo "✅ L'Œil de Dieu redémarré."
