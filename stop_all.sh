#!/data/data/com.termux/files/usr/bin/bash
tmux kill-server 2>/dev/null
pkill -f "ia_|main\.py|play_2captcha" 2>/dev/null
echo "✅ Tous les processus et sessions tmux arrêtés."
