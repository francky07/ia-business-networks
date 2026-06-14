#!/data/data/com.termux/files/usr/bin/bash
tmux kill-session -t ia_reelle 2>/dev/null
cd ~/ia_mainnet_reelle
tmux new-session -d -s ia_reelle "python main.py"
echo "✅ Module réel lancé (session ia_reelle)"
