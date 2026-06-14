#!/data/data/com.termux/files/usr/bin/bash
cd ~
tmux kill-session -t ia_net 2>/dev/null
tmux new-session -d -s ia_net "python ia_net.py"
sleep 2
echo "✅ Bot démarré. Logs: tmux attach -t ia_net"
