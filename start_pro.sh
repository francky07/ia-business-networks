#!/data/data/com.termux/files/usr/bin/bash
cd ~
tmux kill-session -t ia_net 2>/dev/null
tmux kill-session -t booster 2>/dev/null
tmux new-session -d -s ia_net "python ia_net_pro.py"
tmux new-session -d -s booster "python ia_booster_pro.py"
echo "✅ IA NetSolutions PRO (1000 agents) lancée. Logs: tmux attach -t ia_net"
