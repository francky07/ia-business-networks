#!/data/data/com.termux/files/usr/bin/bash
cd ~
for s in ia_net booster booster_pro hub hub_client opp_auto; do
    tmux kill-session -t $s 2>/dev/null || true
done
tmux new-session -d -s ia_net "python ia_net_pro.py"
tmux new-session -d -s booster "python ia_booster_pro.py"
tmux new-session -d -s booster_pro "python ia_booster_pro_250.py"
tmux new-session -d -s hub "python ia_hub_advanced.py"
tmux new-session -d -s hub_client "python hub_client_advanced.py"
tmux new-session -d -s opp_auto "python ia_opp_autonomous.py"
echo "✅ IA NetSolutions (bot + boosters + hub + annexe) lancé"
