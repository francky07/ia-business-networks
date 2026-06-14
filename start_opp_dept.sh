#!/data/data/com.termux/files/usr/bin/bash
# Lancement du département Opportunité & Objectivité (1000 agents)

tmux kill-session -t opp_agents 2>/dev/null
tmux kill-session -t opp_booster 2>/dev/null

tmux new-session -d -s opp_agents "python ia_opp_agents.py"
tmux new-session -d -s opp_booster "python ia_opp_booster.py"

echo "✅ Département Opportunité & Objectivité lancé (500 actifs + 500 booster)"
echo "📌 Logs des agents : tmux attach -t opp_agents"
echo "📌 Logs du booster : tmux attach -t opp_booster"
echo "📌 Pour arrêter : tmux kill-session -t opp_agents ; tmux kill-session -t opp_booster"
