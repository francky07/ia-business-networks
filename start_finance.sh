#!/data/data/com.termux/files/usr/bin/bash
tmux kill-session -t finance 2>/dev/null
tmux kill-session -t finance_booster 2>/dev/null
tmux new-session -d -s finance "python ia_finance_500.py"
tmux new-session -d -s finance_booster "python ia_finance_booster_500.py"
echo "✅ Département indépendance financière lancé (500 agents + 500 booster)"
echo "📌 Logs agents   : tmux attach -t finance"
echo "📌 Logs booster  : tmux attach -t finance_booster"
